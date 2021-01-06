from gameserver.netobj import NetObj
import asyncio
import websockets
import json

class GameClient:
    clientCount = 1

    def __init__(self, sessionId):
        super().__init__()
        self.conn = None
        self.sessionId = sessionId
        self._conn = None
        self._id = GameClient.clientCount
        GameClient.clientCount += 1
        self.username = f'Default {self.id}'
        self.eventLoop = asyncio.get_event_loop()

    @property
    def id(self):
        return self._id
    
    @property
    def connected(self):
        return self._conn.open

    def close(self):
        if self._conn:
            asyncio.run_coroutine_threadsafe(self._conn.close(), self.eventLoop)
            self._conn = None

    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self._conn = conn
        asyncio.run_coroutine_threadsafe(self.recv(), self.eventLoop)
        self.send({'D': 0, 'P': 'connected', 'A': [], 'K': {}})

    
    def send(self, message: dict):
        if self._conn:
            asyncio.run_coroutine_threadsafe(self._conn.send(json.dumps(message)), self.eventLoop)

    async def recv(self):
        conn = self._conn
        while conn and conn.open:
            try:
                message = json.loads(await conn.recv())
            except (websockets.ConnectionClosedError, json.JSONDecodeError):
                await conn.close()
                if conn == self._conn:
                    self._conn = None
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
