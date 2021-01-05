import typing
import websockets
import multiprocessing
import threading
import time
import asyncio
import requests
import functools
import json
import gameserver.logging as logging
from gameserver.netobj import NetObj
from gameserver.gameclient import GameClient

CLOSE_SLEEP = .5
ROUTER_SLEEP = .01
UPDATE_DELAY = 25
logger = logging.getLogger('GameServer')

class GameServer(NetObj):
    def __init__(self, port: int, serverAddress: str, name: str, maxGames: typing.Optional[int] = 4, maxPlayers: typing.Optional[int] = 12, password: typing.Optional[str] = ''):
        super().__init__()
        self.serverAddress = serverAddress
        self.name = name
        self.maxGames = maxGames
        self.maxPlayers = maxPlayers
        self.password = password
        self.running = True
        self._port = port
        self._sessions = {}
        self._games = {}
        self._netQueueHandlerThread = threading.Thread(target=self.netQueueHandler, daemon=True)
        NetObj.setup(0, multiprocessing.Queue())

        logger.log(30, "Gameserver starting")
        self._netQueueHandlerThread.start()
        self.eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.eventLoop)
        self.eventLoop.create_task(self.registerServer())
        self.wsServerCoro = websockets.serve(self.accept, host='', port=self.port, loop=self.eventLoop)
        self.eventLoop.run_until_complete(self.wsServerCoro)
        try:
            self.eventLoop.run_forever()
        finally:
            self.eventLoop.close()

    @property
    def port(self):
        return self.port

    @property
    def playerCount(self):
        return len([player for player in self.sessions if player.conn])

    async def netQueueHandler(self):
        logger.log(30, "Router started")
        while self.running:
            time.sleep(ROUTER_SLEEP)
            while not self.netQueue.empty():
                message = self.netQueue.get()
                if message['D'] == 0:
                    #From game to The server
                    message['D'] = self.id
                    NetObj.handleClientRpc(message)
                elif message['S'] == 0:
                    #From gameclient, going to remote client
                    player = self._sessions[message['D'], None]
                    if player:
                        message.pop('C')
                        message.pop('S')
                        message['D'] = 0
                        player.send(message)
                elif message['C'] == 0:
                    #Directed to all clients of game
                    players = self._games.get(message['S'], (None, []))[1]
                    message.pop('C')
                    message.pop('S')
                    for player in players:
                        player.send(message)
                elif message['C'] in self._sessions:
                    #Directed to single client of game
                    player = self._sessions[message['C'], None]
                    if player:
                        message.pop('C')
                        message.pop('S')
                        player.send(message)

    async def registerServer(self):
        logger.log(30, "Register")
        while self.running:
            if self.id is None:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/register', json = 
                {'name': self.name, 'port': self.port, 'maxGames': self.maxGames, 'maxPlayers': self.maxPlayers, 'password': self.password != ''}))
                try:
                    res = await req
                    if res.status_code == 201:
                        self.id = res.json()['id']
                        logger.log(20, "Registered with server")
                except requests.exceptions.ConnectionError:
                    logger.log(40, "Failed to connect to server for registration")
            else:
                req = self.eventLoop.run_in_executor(None, functools.partial(requests.post, f'{self.serverAddress}/server/{self.id}/update', json = 
                {'currentGames': len(self.lobbies), 'currentPlayers': self.playerCount}))
                try:
                    res = await req
                    if res.status_code != 200:
                        logger.log(40, "Lost connecton with main server")
                        self.id = None
                except requests.exceptions.ConnectionError:
                    logger.log(30, "Failed to connect to server for update")
            await asyncio.sleep(UPDATE_DELAY)

    def close(self):
        logger.log(30, "Closing server")
        self.running = False
        for game in self._games.values():
            game.close()
        for client in self.sessions.values():
            client.close()
        async def finishClose(self):
            await self.wsServerCoro.wait_closed()
            self.loop.stop()
        self.eventLoop.create_task(finishClose(self))
        if self._netQueueHandlerThread and self._netQueueHandlerThread.isAlive():
            self._netQueueHandlerThread.join()

    async def accept(self, conn, url):
        '''Called on incomming connections, waits for session id to be sent
        '''
        try:
            message = json.loads(await conn.recv())
        except (websockets.ConnectionClosedError, json.JSONDecodeError):
            message = None
        try:
            if self.playerCount < self.maxPlayers:
                if message['SID'] in self.sessions:
                    self.sessions[message['SID']].setConn(conn)
                    return
                elif message['PASSWORD'] == self.password:
                    self.sessions[message['SID']] = GameClient(message['SID'], self)
                    self.sessions[message['SID']].setConn(conn)
                    return
        except KeyError:
            pass
        await conn.close()
