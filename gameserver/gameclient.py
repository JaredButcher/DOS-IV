from gameserver.netobj import NetObj
import asyncio
import websockets
import json

class GameClient:
    clientCount = 1

    def __init__(self, sessionId):
        super().__init__()
        self.conn = None
        self.username = "Default Name"
        self.game = None
        self.sessionId = sessionId
        self._conn = None
        self._id = GameClient.clientCount
        GameClient.clientCount += 1
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
        while self._conn and self._conn.open:
            try:
                message = json.loads(await self._conn.recv())
            except (websockets.ConnectionClosedError, json.JSONDecodeError):
                self.close()
                return
            if message:
                message['S'] = self.id
                if message['D'] == 0:
                    self.handleMessage(message)
                elif self.game:
                    self.game.send(message)

    def handleMessage(self, message: dict):
        pass
