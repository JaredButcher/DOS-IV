import multiprocessing
import threading
import time
import typing
from gameserver.netobj import NetObj, TARGET

ROUTER_SLEEP = .01

class GameBase(NetObj):
    def __init__(self, serverId: int, serverQueue: 'multiprocessing.Queue', gameQueue: 'multiprocessing.Queue', owner: int, password: typing.Optional(str) = ''):
        super().__init__()
        self.serverId = serverId
        self.serverQueue = serverQueue
        self.gameQueue = gameQueue
        self.running = True
        self.gameLoopRunning = False
        self.tickRate = 20
        self.owner = owner
        self.password = password
        self.players = {}
        NetObj.setup(self.send)
        self.routerLoop()

    def routerLoop(self):
        while self.running:
            time.sleep(ROUTER_SLEEP)
            while not self.gameQueue.empty():
                message = self.gameQueue.get()
                if message['D'] == 0:
                    message['D'] = self.id
                NetObj.handleClientRpc(message)
        
    def gameLoop(self, deltatime: float):
        pass

    def startGameLoop(self):
        def run():
            lastTime = time.time()
            while self.running and self.gameLoopRunning:
                delay = 1 / self.tickRate - (time.time() - lastTime)
                if delay > 0: time.sleep(delay)
                beginTime = time.time()
                self.gameLoop(lastTime - beginTime)
                lastTime = beginTime
        self.gameLoopRunning = True
        self._gameQueueHandleThread = threading.Thread(target=run, daemon=True)
        self._gameQueueHandleThread.start()

    def stopGameLoop(self):
        self.gameLoopRunning = False
        
    def send(self, target: 'TARGET', message: dict, client: typing.Optional[int] = 0):
        self.serverQueue.put((self.serverId, target, message, client))
