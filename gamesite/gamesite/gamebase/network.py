import websockets
import asyncio
import multiprocessing
from .taskProcess import TaskProcess
import json

CLOSE_POLL_RATE = 30

class GameServer(TaskProcess):
    '''Listens to socket requests, forwards them to respective games, and spawns games. Runs a socket server on a seperate process.
    '''
    def __init__(self, port):
        '''Create and start server
        Args:
            port (int): port to listen to
        '''
        self.parentNetPipe, self.childNetPipe = multiprocessing.Pipe()
        self.port = port
        self.clients = []
        self.games = []
        super().__init__()

    def processStart(self):
        self.eventLoop = asyncio.get_event_loop()
        self.wsServerCoro = self.eventLoop.run_until_complete(websockets.serve(self.accept, host='', port=self.port, loop=self.eventLoop))
        self.eventLoop.call_soon(self._close)
        self.eventLoop.run_forever()

    async def accept(self, conn, url):
        '''Ran asyncrnously on child process, called on incoming connections
        '''
        client = GameClient(self, conn)
        self.clients.append(client)
        await client.recv()

    def _close(self):
        '''Called CLOSE_POLL_RATE times per second, checks if the server has been told to stop and stops it
        '''
        if self.stopEvent.is_set():
            for game in self.games:
                game.close()
            self.wsServerCoro.close()
            async def finishClose(self):
                await self.wsServerCoro.wait_closed()
                self.loop.stop()
            self.eventLoop.create_task(self.finishClose())
        else:
            self.eventLoop.call_later(1/CLOSE_POLL_RATE, self._close)

class GameClient():
    '''A user's socket connection, used to send messages to user and await messages
    '''
    def __init__(self, server, conn):
        self.server = server
        self.conn = conn
        self.sessionId = 0
        self.belongsTo = None
    
    async def recv(self):
        while not self.server.stopEvent.is_set():
            try:
                message = await self.conn.recv()
            except websockets.exceptions.ConnectionClosed:
                self.close()
                return
    
    def send(self, message):
        asyncio.run_coroutine_threadsafe(self.conn.send(message), self.server.eventLoop)
            
    def close(self):
        self.conn.close()
        self.server.clients.remove(self)
        if self.belongsTo:
            self.belongsTo.removePlayer(self)

    def clientId(self):
        '''Get the client's sesson id
        Returns:
            (int): session id, 0 if not known
        '''
        return self.sessionId

    def setBelongsTo(self, group):
        '''Sets the group that this player currently belongs to allow it to be notified if we disconnect
        Args:
            group (Lobby | Game | None): group this client currently belongs to
        '''
        self.belongsTo = group

class Message():
    '''Universal form for messages, used to pack and unpack messages
    '''
    @staticmethod
    def parseMessage(message):
        '''Parse received json string into message object
        '''
        data = json.loads(message)
        return Message(data["user"], data["game"], data["form"], data["content"])

    def __init__(self, user, game, form, content):
        '''Create a new message
        Args:
            user (int): session id of user
            game (int): game id to send to, 0 if no game
            form (string): type of message
            content (object): any message content
        '''
        self.user = user
        self.game = game
        self.form = form
        self.content = content

    def __str__(self):
        return json.dumps({"user": self.user, "game": self.game, "form": self.form, "content": self.content})

    def toString(self):
        '''Packs message into sendable string
        '''
        return str(self)
    