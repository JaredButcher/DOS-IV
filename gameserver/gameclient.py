from gameserver.netobj import NetObj
import asyncio
import websockets
import json

class GameClient(NetObj):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.username = "Default Name"
        self.game = None
        self.eventLoop = asyncio.get_event_loop()

    def close(self):
        if self.conn:
            asyncio.run_coroutine_threadsafe(self.conn.close(), self.eventLoop)
            self.conn = None

    def setConn(self, conn: 'websockets.WebSocketServerProtocol'):
        self.close()
        self.conn = conn
        asyncio.run_coroutine_threadsafe(self.recv(), self.eventLoop)
    
    def send(self, message: dict):
        if self.conn:
            asyncio.run_coroutine_threadsafe(self.conn.send(json.dumps(message)), self.eventLoop)

    async def recv(self):
        while self.conn and self.conn.open:
            try:
                message = json.loads(await self.conn.recv())
            except (websockets.ConnectionClosedError, json.JSONDecodeError):
                self.close()
                return
            if message:
                message['S'] = self.id
                if message['D'] == 0:
                    message['D'] = self.id
                    NetObj.handleClientRpc(message)
                elif self.game:
                    self.game.send(message)

