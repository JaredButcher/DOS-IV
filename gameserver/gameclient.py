import asyncio
import typing
import websockets
import json
import logging
from gameserver.netobj import NetObj

logger = logging.getLogger('GameClient')

class GameClient:
    '''Holds a user id, the connection to the client, and some data that is persistent between games. 
    '''
    clientCount = 1

    def __init__(self, sessionId):
        self.sessionId = sessionId
        self._conn = None
        self.onDisconnect = None
        self._id = GameClient.clientCount
        GameClient.clientCount += 1
        self.username = f'Username {self.id}'
        self.owner = False

    @property
    def id(self):
        return self._id
    
    @property
    def connected(self):
        return self._conn.open if self._conn else False

    def close(self, message: typing.Optional[dict] = None):
        '''Close the socket, can optionaly send a message before closeure
        '''
        if self._conn:
            logging.log(20, f'Connection closed to client {self._id}')
            async def close(conn):
                if message:
                    await conn.send(json.dumps(message))
                await conn.close()
            asyncio.create_task(close(self._conn))
            self._conn = None
            if self.onDisconnect:
                self.onDisconnect(self)

    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self._conn = conn
        self.send({'D': 0, 'P': 'connected', 'A': [self.id]})

    def send(self, message: dict):
        if self._conn:
            asyncio.create_task(self._conn.send(json.dumps(message)))

    async def recv(self, onRecv: typing.Callable[[dict], None]):
        conn = self._conn
        while conn and conn.open:
            try:
                message = json.loads(await conn.recv())
            except (websockets.ConnectionClosed, json.JSONDecodeError):
                self.close()
                return
            if message:
                logging.log(30, message)
                message['S'] = self.id
                try:
                    onRecv(message, self.owner)
                except KeyError:
                    await conn.send(json.dumps({'D': 0, 'P': 'disconnected', 'A': ['Malformed message']}))
                    self.close()
