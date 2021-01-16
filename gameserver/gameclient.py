from websockets.exceptions import ConnectionClosedOK
from gameserver.netobj import NetObj
import asyncio
import websockets
import json
import logging
import collections

logger = logging.getLogger('GameClient')

class GameClient(collections.UserDict):
    clientCount = 1

    def __init__(self, sessionId):
        super().__init__()
        self.conn = None
        self.sessionId = sessionId
        self._conn = None
        self._id = GameClient.clientCount
        self.onDisconnect = None
        GameClient.clientCount += 1
        self.username = f'Default {self.id}'

    @property
    def id(self):
        return self._id
    
    @property
    def connected(self):
        return self._conn.open if self._conn else False

    def close(self):
        if self._conn:
            logging.log(20, f'Lost connection to client {self._id}')
            asyncio.create_task(self._conn.close())
            self._conn = None
            if self.onDisconnect:
                self.onDisconnect(self)

    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self._conn = conn
        asyncio.create_task(self.recv())
        self.send({'D': 0, 'P': 'connected', 'A': [self.id]})

    
    def send(self, message: dict):
        if self._conn:
            logging.log(30, json.dumps(message))
            asyncio.create_task(self._conn.send(json.dumps(message)))

    async def recv(self):
        conn = self._conn
        while conn and conn.open:
            try:
                message = json.loads(await conn.recv())
            except (websockets.ConnectionClosed, json.JSONDecodeError):
                self.close()
                return
            if message:
                message['S'] = self.id
                if message['D'] == 0:
                    self.handleMessage(message)
                else:
                    try:
                        NetObj.handleClientRpc(message)
                    except KeyError:
                        await conn.send(json.dumps({'D': 0, 'P': 'disconnected', 'A': ['Malformed message'], 'K': {}}))
                        self.close()

    def handleMessage(self, message: dict):
        pass
