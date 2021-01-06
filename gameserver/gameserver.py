import typing
import websockets
import asyncio
import requests
import functools
import json
import logging
import multiprocessing
from gameserver.logging import initLogging
from gameserver.netobj import NetObj
from gameserver.gameclient import GameClient
from gameserver.gamebase import GameBase

CLOSE_SLEEP = .5
ROUTER_SLEEP = .01
UPDATE_DELAY = 25
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
        self._sessions = {}
        self._game = None
        self._wsServer = None
        self.start()

    def run(self):
        initLogging(self.logLevel, self.logFile)
        logger.log(30, "Gameserver starting")
        self.isChildProcess = True
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

    @property
    def port(self):
        return self._port

    @property
    def playerCount(self):
        if self._game:
            return self._game.playerCount
        else:
            return len([player for player in self._sessions.values() if player.connected])

    @property
    def maxPlayers(self):
        if self._game:
            return self._game.maxPlayers
        else:
            return 1

    def handleMessage(self, source: int, message: dict):
        pass

    async def registerServer(self):
        logger.log(20, "Register loop starting")
        while self.running:
            if self.id is None:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/register', json = 
                {'name': self.name, 'port': self.port, 'maxPlayers': self.maxPlayers, 'password': self.password != '', 'currentPlayers': self.playerCount, 'game': self._game.gameName if self._game else 'None'}, timeout=.3))
                try:
                    res = await req
                    if res.status_code == 201:
                        self.id = res.json()['id']
                        logger.log(20, "Registered with server")
                except requests.exceptions.ConnectionError:
                    logger.log(40, "Failed to connect to server for registration")
            else:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/{self.id}/update', json = 
                {'currentPlayers': self.playerCount, 'maxPlayers': self.maxPlayers, 'game': self._game.gameName if self._game else 'None'}, timeout=.3))
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
            for client in self._sessions.values():
                client.close()
        else:
            self.closeEvent.set()

    async def accept(self, conn, url):
        '''Called on incomming connections, waits for session id to be sent
        '''
        logger.log(20, f'Received new connection')
        if not self.running: return
        try:
            message = json.loads(await conn.recv())
        except (websockets.ConnectionClosedError, json.JSONDecodeError):
            return
        if not self.running and message and self.playerCount < self.maxPlayers: return
        try:
            if message['SID'] in self._sessions.keys():
                self._sessions[message['SID']].setConn(conn)
            elif message['PASSWORD'] == self.password:
                self._sessions[message['SID']] = GameClient(message['SID'])
                self._sessions[message['SID']].setConn(conn)
            else:
                return
        except KeyError:
            return
        if self._game:
            if not self._game.tryAddPlayer(self._sessions[message['SID']]):
                self._sessions[message['SID']].close()

