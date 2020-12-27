import websockets
import asyncio
import multiprocessing
import gamesite.gamebase.taskProcess as taskProcess
import gamesite.gamebase.networkenums as netenums
from gamesite.gamebase.message import Message
from gamesite.gamebase.lobby import Lobby
import json
import logging
import typing
import collections

CLOSE_SLEEP = .5
ROUTER_SLEEP = .1
logger = logging.getLogger('GameServer')

class GameServer(taskProcess.TaskProcess):
    '''Listens to socket requests, forwards them to respective games, and spawns games. Runs a socket server on a seperate process.
    '''
    def __init__(self, port):
        '''Create and start server
        Args:
            port (int): port to listen to
        '''
        self.port = port
        self.sessions = {}
        self.lobbies = {}
        super().__init__(multiprocessing.Queue(), name="GameServer")

    def run(self):
        self.eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.create_task(self.route())
        self.wsServerCoro = self.eventLoop.run_until_complete(websockets.serve(self.accept, host='', port=self.port, loop=self.eventLoop))
        try:
            self.eventLoop.run_forever()
        finally:
            self.eventLoop.close()

    def removeClient(self, client):
        client = self.sessions.pop(client.id, None)
        if client:
            client.close()

    async def accept(self, conn, url):
        '''Ran asyncrnously on child process, called on incoming connections
        '''
        try:
            message = Message.parseMessage(await conn.recv())
        except websockets.ConnectionClosedError:
            await conn.close()
            return
        if message.matches(netenums.CHANNEL.SERVER.value, 0, netenums.NETWORK_FORMS.REGISTER):
            sessionId = message['content']['sessionId']
            if sessionId in self.sessions:
                self.sessions[sessionId].setConn(conn)
            else:
                self.sessions[sessionId] = GameClient(sessionId, self)
        else:
            await conn.close()

    async def route(self):
        while not self.stopEvent.is_set():
            await asyncio.sleep(ROUTER_SLEEP)
            while not self.networkQueue.empty():
                message = Message.parseMessage(self.networkQueue.get())
                if message:
                    if message.matches(netenums.CHANNEL.SERVER.value):
                        self.networkHandler(message)
                    elif message.matches(netenums.CHANNEL.LOBBY.value):
                        lobby = self.LOBBY.get(message['des'], None)
                        if lobby:
                            lobby.handle(message)
                    elif message.matches(netenums.CHANNEL.CLIENT.value):
                        client = self.sessions.get(message['des'], None)
                        if client:
                            client.send(message)
        await self.close()

    async def close(self):
        for game in self.games:
            game.close()
        for client in self.sessions.values:
            client.close()
        self.wsServerCoro.close()
        async def finishClose(self):
            await self.wsServerCoro.wait_closed()
            self.loop.stop()
        self.eventLoop.create_task(self.finishClose())

    def put(self, message: str):
        self.networkQueue.put(message)
        
    def networkHandler(self, message):
        pass

    def addLobby(self, lobby: 'Lobby'):
        self.lobbies[lobby.id] = lobby

    def rmLobby(self, lobbyId: int):
        self.lobbies.pop(lobbyId)

class GameClient(collections.UserDict):
    '''A user's session, will store its current socket
    '''

    def __init__(self, sessionId: int, server: 'GameServer'):
        self.server = server
        self.conn = None
        self.sessionId = sessionId
        self.lobby = None
    
    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self.conn = conn
        asyncio.run_coroutine_threadsafe(self.recv(), self.server.eventLoop)

    async def recv(self):
        while not self.server.stopEvent.is_set():
            try:
                message = Message.parseMessage(await self.conn.recv())
            except websockets.ConnectionClosedError:
                self.close()
                return
            #Ready it for routing
            message['src'] = self.sessionId
            if message.matches(channel=netenums.CHANNEL.GAME.value):
                message['des'] = self.lobby.id
            else:
                message['des'] = 0
            self.server.put(str(message))

    @property
    def id(self):
        return self.sessionId
    
    def send(self, message: typing.Union[str, 'Message']):
        if self.conn:
            asyncio.run_coroutine_threadsafe(self.conn.send(message), self.server.eventLoop)

    def setLobby(self, lobby: 'Lobby'):
        self.lobby = lobby
            
    def close(self):
        if self.lobby:
            self.lobby.removePlayer(self.id)
        if self.conn:
            asyncio.run_coroutine_threadsafe(self.conn.close(), self.server.eventLoop)
            self.conn = None
    