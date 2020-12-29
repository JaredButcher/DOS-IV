import multiprocessing
import websockets
import asyncio
import gameserver.serverenums as serverenums
from gameserver.message import Message
from gameserver.lobby import Lobby
import logging
import typing
import random
import requests
import json
import functools

CLOSE_SLEEP = .5
ROUTER_SLEEP = .1
UPDATE_DELAY = 25
logger = logging.getLogger('GameServer')

random.seed()

class GameServer:
    '''Listens to socket requests, forwards them to respective games, and spawns games. Runs a socket server on a seperate process.
    '''
    def __init__(self, port: int, serverAddress: str, name: str, maxGames: int, maxPlayers: int):
        '''Create and start server
        Args:
            port (int): port to listen to
        '''
        self.port = port
        self.serverAddress = serverAddress
        self.name = name
        self.id = None
        self.maxGames = maxGames
        self.maxPlayers = maxPlayers
        self.sessions = {}
        self.lobbies = {}
        self.registered = False
        self.running = True
        self.inQueue = multiprocessing.Queue()

    def run(self):
        logger.log(30, "Run")
        self.eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.create_task(self.routeLobbyMessages())
        self.eventLoop.create_task(self.registerServer())
        self.wsServerCoro = websockets.serve(self.accept, host='', port=self.port, loop=self.eventLoop)
        self.eventLoop.run_until_complete(self.wsServerCoro)
        try:
            self.eventLoop.run_forever()
        finally:
            self.eventLoop.close()

    def createLobby(self, name: str, owner: str, password: typing.Optional[str] = '') -> 'Lobby':
        while True:
            id = random.getrandbits(32)
            if id not in self.lobbies: break
        lobby = self.lobbies[id] = Lobby(self, id, name, owner, password)
        self.sessions[owner].setLobby(lobby, password)
        return lobby

    def closeLobby(self, lobbyId: int):
        lobby = self.lobbies.pop(lobbyId, None)
        if lobby:
            lobby.stop()

    def handleLobbyMessage(self, message: 'Message'):
        if message['F'] == serverenums.ServerForms.LOG.value and message.contains(('LEVEL', 'MSG')):
            logger.log(message['LEVEL'], message['MSG'])

    def handleClientMessage(self, message: 'Message'):
        pass

    async def routeLobbyMessages(self):
        logger.log(30, "Route")
        while self.running:
            await asyncio.sleep(ROUTER_SLEEP)
            while not self.inQueue.empty():
                message = self.inQueue.get()
                if message['C'] == serverenums.Channels.SERVER.value:
                    self.handleLobbyMessage(message)
                elif message['C'] == serverenums.Channels.CLIENT.value or message['C'] == serverenums.Channels.CLIENT_GAME.value:
                    if 'SID' in message and message['SID'] in self.sessions:
                        self.sessions[message['SID']].outHandle(message)

    async def accept(self, conn, url):
        '''Called on incomming connections, waits for session id to be sent
        '''
        try:
            message = Message.parseMessage(await conn.recv())
        except websockets.ConnectionClosedError:
            message = None
        if message and message['C'] == serverenums.Channels.SERVER.value and 'SID' in message:
            if message['SID'] not in self.sessions:
                self.sessions[message['SID']] = GameClient(message['SID'], self)
            self.sessions[message['SID']].setConn(conn)
        else:
            await conn.close()

    def close(self):
        self.running = False
        for lobby in self.lobbies.values():
            self.closeLobby(lobby.id)
        for client in self.sessions.values():
            client.close()
        async def finishClose(self):
            await self.wsServerCoro.wait_closed()
            self.loop.stop()
        self.eventLoop.create_task(finishClose(self))

    async def registerServer(self):
        logger.log(30, "Register")
        while self.running:
            if self.id is None:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/register', json = 
                {'name': self.name, 'port': self.port, 'maxGames': self.maxGames, 'maxPlayers': self.maxPlayers}))
                res = await req
                if res.status_code == 201:
                    self.id = res.json()['id']
                    logger.log(30, "Registered with server")
            else:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/{self.id}/update', json = 
                {'currentGames': len(self.lobbies), 'currentPlayers': len(self.sessions)}))
                res = await req
                if res.status_code != 200:
                    logger.log(30, "Lost connecton with main server")
                    self.id = None
            await asyncio.sleep(UPDATE_DELAY)

class GameClient:
    '''A user's ws session
    '''
    def __init__(self, sessionId: str, server: 'GameServer'):
        self.server = server
        self.conn = None
        self.username = "Default Name"
        self.sessionId = sessionId
        self.lobby = None
    
    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self.conn = conn
        asyncio.run_coroutine_threadsafe(self.recv(), self.server.eventLoop)

    async def recv(self):
        while True:
            try:
                message = Message.parseMessage(await self.conn.recv())
            except websockets.ConnectionClosedError:
                self.close()
                return
            if message:
                message['SID'] = self.sessionId
                if message['C'] == serverenums.Channels.CLIENT.value:
                    self.inHandle(message)
                elif message['C'] == serverenums.Channels.SERVER.value:
                    self.server.handleClientMessage(message)
                elif message['C'] == serverenums.Channels.GAME.value or message['C'] == serverenums.Channels.LOBBY.value:
                    if self.lobby:
                        self.lobby.put(message)
            
    def inHandle(self, message: 'Message'):
        if message['F'] == serverenums.InClientForms.SET_USERNAME.value and message.contains(('USERNAME',)):
            self.username = message['USERNAME']

    def outHandle(self, message: 'Message'):
        if message['C'] == serverenums.Channels.CLIENT.value:
            if message['F'] == serverenums.OutClientForms.LOBBY.value:
                if message['ID'] == 0:
                    self.lobby = None
                else:
                    self.lobby = message['ID']
        self.send(message)
    
    def send(self, message: 'Message'):
        if self.conn:
            message.pop('C', None)
            message.pop('SID', None)
            asyncio.run_coroutine_threadsafe(self.conn.send(str(message)), self.server.eventLoop)
            
    def close(self):
        if self.conn:
            asyncio.run_coroutine_threadsafe(self.conn.close(), self.server.eventLoop)
            self.conn = None
