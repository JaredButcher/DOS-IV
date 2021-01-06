import typing
import websockets
import multiprocessing
import threading
import time
import asyncio
import requests
import functools
import json
import logging
from gameserver.netobj import NetObj, TARGET
from gameserver.gameclient import GameClient

CLOSE_SLEEP = .5
ROUTER_SLEEP = .01
UPDATE_DELAY = 1
logger = logging.getLogger('GameServer')

class GameServer:
    def __init__(self, port: int, serverAddress: str, name: str, maxGames: typing.Optional[int] = 4, maxPlayers: typing.Optional[int] = 12, password: typing.Optional[str] = ''):
        super().__init__()
        self.serverAddress = serverAddress
        self.name = name
        self.maxGames = maxGames
        self.maxPlayers = maxPlayers
        self.password = password
        self.running = True
        self.netQueue = multiprocessing.Queue()
        self.id = None
        self._port = port
        self._sessions = {}
        self._games = {}
        self._netQueueHandlerThread = threading.Thread(target=self.netQueueHandler, daemon=True)

    @property
    def port(self):
        return self._port

    @property
    def playerCount(self):
        return len([player for player in self._sessions.values() if player.connected])

    def start(self):
        logger.log(30, "Gameserver starting")
        self._netQueueHandlerThread.start()
        self.eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.create_task(self.registerServer())
        self.wsServerCoro = websockets.serve(self.accept, host='', port=self.port)
        self.thing = self.eventLoop.run_until_complete(self.wsServerCoro)
        try:
            self.eventLoop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    def netQueueHandler(self):
        logger.log(20, "Router loop starting")
        while self.running:
            time.sleep(ROUTER_SLEEP)
            while not self.netQueue.empty():
                message = self.netQueue.get()
                if message[0] == TARGET.SERVER:
                    self.handleMessage(message[1], message[2])
                elif message[0] == TARGET.CLIENT:
                    player = self._sessions[message[3], None]
                    if player:
                        player.send(message[2])
                elif message[0] == TARGET.ALL_CLIENTS:
                    game = self._games.get(message[1], None)
                    if game:
                        for player in game.players:
                            player.send(message[2])

    def handleMessage(self, source: int, message: dict):
        pass

    async def registerServer(self):
        logger.log(20, "Register loop starting")
        while self.running:
            if self.id is None:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/register', json = 
                {'name': self.name, 'port': self.port, 'maxGames': self.maxGames, 'maxPlayers': self.maxPlayers, 'password': self.password != ''}, timeout=.3))
                try:
                    res = await req
                    if res.status_code == 201:
                        self.id = res.json()['id']
                        logger.log(20, "Registered with server")
                except requests.exceptions.ConnectionError:
                    logger.log(40, "Failed to connect to server for registration")
            else:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/{self.id}/update', json = 
                {'currentGames': len(self._games), 'currentPlayers': self.playerCount}, timeout=.3))
                try:
                    res = await req
                    if res.status_code != 200:
                        logger.log(40, "Lost connecton with main server")
                        self.id = None
                except requests.exceptions.ConnectionError:
                    logger.log(30, "Failed to connect to server for update")
            await asyncio.sleep(UPDATE_DELAY)

    def close(self):
        logger.log(20, "Closing server")
        self.running = False
        for game in self._games.values():
            game.close()
        for client in self._sessions.values():
            client.close()
        self.thing.close()
        if self._netQueueHandlerThread and self._netQueueHandlerThread.isAlive():
            self._netQueueHandlerThread.join()

    async def accept(self, conn, url):
        '''Called on incomming connections, waits for session id to be sent
        '''
        logger.log(20, f'Received new connection')
        try:
            message = json.loads(await conn.recv())
        except (websockets.ConnectionClosedError, json.JSONDecodeError):
            message = None
        if message and self.playerCount < self.maxPlayers:
            try:
                if message['SID'] in self._sessions.keys():
                    self._sessions[message['SID']].setConn(conn)
                    return
                elif message['PASSWORD'] == self.password:
                    self._sessions[message['SID']] = GameClient(message['SID'])
                    self._sessions[message['SID']].setConn(conn)
                    return
            except KeyError:
                pass
        await conn.close()
