import typing
import websockets
import asyncio
import requests
import functools
import json
import logging
import multiprocessing
from gameserver.logging import initLogging
from gameserver.gameclient import GameClient
from gameserver.gamebase import GameBase
from gameserver.netobj import NetObj

CLOSE_SLEEP = .5
ROUTER_SLEEP = .01
UPDATE_DELAY = 15
logger = logging.getLogger('GameServer')

class GameServer(multiprocessing.Process):
    def __init__(self, port: int, serverAddress: str, name: str, password: typing.Optional[str] = '', logLevel: typing.Optional[int] = 20, logFile: typing.Optional[str] = '', **kwargs):
        super().__init__(name=name, daemon=True, **kwargs)
        self.serverAddress = serverAddress
        self.name = name
        self.password = password
        self.running = True
        self.id = None
        self.logLevel = logLevel
        self.logFile = logFile
        self.closeEvent = multiprocessing.Event()
        self.isChildProcess = False
        self._port = port
        self._clients = {}
        self._game = None
        self._wsServer = None
        self.start()

    @property
    def port(self):
        return self._port

    @property
    def connectedClients(self):
        return [client for client in self._clients.values() if client.connected]

    def run(self):
        initLogging(self.logLevel, self.logFile)
        logger.log(30, f'Gameserver {self.name} starting')
        self.isChildProcess = True
        NetObj.send = self.send
        self._game = GameBase()
        self.eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.create_task(self.registerServer())
        self._wsServer = self.eventLoop.run_until_complete(websockets.serve(self.accept, host='', port=self.port))
        try:
            self.eventLoop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    async def registerServer(self):
        logger.log(20, "Register loop starting")
        while self.running:
            if self.id is None:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/register', json = 
                {'name': self.name, 'port': self.port, 'maxPlayers': self._game.maxPlayers, 'password': self.password != '', 'currentPlayers': self._game.playerCount, 'game': self._game.gameName if self._game else 'None'}, timeout=.3))
                try:
                    res = await req
                    if res.status_code == 201:
                        self.id = res.json()['id']
                        logger.log(20, "Registered with server")
                except requests.exceptions.ConnectionError:
                    logger.log(40, "Failed to connect to server for registration")
            else:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/{self.id}/update', json = 
                {'currentPlayers': self._game.playerCount, 'maxPlayers': self._game.maxPlayers, 'game': self._game.gameName if self._game else 'None'}, timeout=.3))
                try:
                    res = await req
                    if res.status_code != 200:
                        logger.log(40, "Lost connecton with main server")
                        self.id = None
                except requests.exceptions.ConnectionError:
                    logger.log(30, "Failed to connect to server for update")
            await asyncio.sleep(UPDATE_DELAY)
            if self.closeEvent.is_set():
                self.running = False

    def close(self):
        if self.isChildProcess:
            logger.log(20, "Closing server")
            self.running = False
            if self._wsServer: self._wsServer.close()
            if self._game: self._game.close()
            for client in self._clients.values():
                client.close()
        else:
            self.closeEvent.set()

    def onRecv(self, message: dict):
        if message['D'] == 0:
            pass
        else:
            des = NetObj.netObjs.get(message['D'], None)
            if des: des.recvCommand(message)

    async def accept(self, conn, url):
        '''Called on incomming connections, waits for session id to be sent
        '''
        logger.log(20, f'Received new connection')
        if not self.running: return
        try:
            message = json.loads(await conn.recv())
        except (websockets.ConnectionClosedError, json.JSONDecodeError):
            return
        try:
            if message['SID'] in self._clients.keys():
                self._clients[message['SID']].setConn(conn)
                self._game.playerConnected(self._clients[message['SID']])
            elif message['PASSWORD'] == self.password:
                self._clients[message['SID']] = GameClient(message['SID'])
                self._clients[message['SID']].setConn(conn)
                self._game.newPlayer(self._clients[message['SID']])
            else:
                return
        except KeyError:
            logger.log(30, f'New Connection KeyError')
            return
        self.updateClient(message['SID'])
        await self._clients[message['SID']].recv()

    def send(self, message: dict, clientId: typing.Optional[int] = None):
        if clientId:
            client = self._clients.get(clientId, None)
            if client: client.send(message)
        else:
            for client in self.connectedClients:
                client.send(message)

    def updateClient(self, clientId: typing.Optional[int] = None):
        messages = []
        for netObj in NetObj.netObjs:
            messages.append(netObj.serialize())
        if clientId:
            client = self._clients.get(clientId, None)
            if client: client.send({'D': 0, 'P': 'update', 'A': [messages]})
        else:
            for client in self.connectedClients:
                client.send({'D': 0, 'P': 'update', 'A': [messages]})

    def clearClient(self, clientId: typing.Optional[int] = None):
        if clientId:
            client = self._clients.get(clientId, None)
            if client: client.send({'D': 0, 'P': 'clear', 'A': []})
        else:
            for client in self.connectedClients:
                client.send({'D': 0, 'P': 'clear', 'A': []})