import websockets
import asyncio
import multiprocessing
import gamesite.gamebase.taskProcess as taskProcess
import gamesite.gamebase.networkenums as netenums
from gamesite.gamebase.message import Message
import json
import logging
from typing import Optional
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
        self.clients = {}
        self.unregClients = []
        self.games = {}
        self.handlers = {}
        self.setHandler(netenums.CHANNEL.SERVER, netenums.SERVER_HANDLERS.NETWORK, self.networkHandler)
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
        client = self.clients.pop(client.id, None)
        if client in self.unregClients: self.unregClients.remove(client)            

    def setHandler(self, channel, id, handler):
        channelHandler = self.handlers.get(channel, {})
        channelHandler[id] = handler
        self.handlers[channel] = channelHandler

    def removeHandler(self, channel, id):
        channelHandler = self.handlers.get(channel, {})
        channelHandler.pop(id)
        self.handlers[channel] = channelHandler

    async def accept(self, conn, url):
        '''Ran asyncrnously on child process, called on incoming connections
        '''
        client = GameClient(self, conn)
        self.unregClients.append(client)
        await client.recv()

    async def route(self):
        while not self.stopEvent.is_set():
            await asyncio.sleep(ROUTER_SLEEP)
            while not self.networkQueue.empty():
                message = Message.parseMessage(self.networkQueue.get())
                handler = self.handlers.get(message['channel'], {}).get(message['des'], None)
                if handler: handler(message)
        for game in self.games:
            game.close()
        self.wsServerCoro.close()
        async def finishClose(self):
            await self.wsServerCoro.wait_closed()
            self.loop.stop()
        self.eventLoop.create_task(self.finishClose())

    def put(self, message: str):
        self.networkQueue.put(message)
        
    def networkHandler(self, message):
        message = Message.parseMessage(message)
        if message['form'] == netenums.NETWORK_FORMS.REGISTER.value:
            #TODO Get session id
            client = None
            self.clients[id] = client
            self.unregClients.remove(client)
            
class GameClient():
    '''A user's socket connection, used to send messages to user and await messages
    '''

    def __init__(self, server: 'gamesite.gamebase.network.GameServer', conn: 'websockets.client'):
        self.server = server
        self.conn = conn
        self.sessionId = 0
        self.lobby = None
    
    async def recv(self):
        while not self.server.stopEvent.is_set():
            try:
                message = Message.parseMessage(await self.conn.recv())
            finally:
                self.close()
                return
            message['source'] = self.id
            if message['channel'] in (CHANNEL.GAME.value,):
                self.server.put(str(message))

    @property
    def id(self):
        return self.sessionId
    
    def send(self, message):
        asyncio.run_coroutine_threadsafe(self.conn.send(message), self.server.eventLoop)
            
    def close(self):
        if self.lobby:
            self.lobby.removePlayer(self.id)
        self.server.removeClient(self)
        asyncio.run_coroutine_threadsafe(self.conn.close(), self.server.eventLoop)
    