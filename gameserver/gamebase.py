from gameserver.gameclient import GameClient
from gameserver.netobj import NetObj
import time
import asyncio

class GameBase(NetObj):
    def __init__(self, owner: 'GameClient'):
        super().__init__()
        self.gameName = "None"
        self.owner = owner
        self.maxPlayers = 1
        self.tickrate = 20
        self.running = False
        self._players = {}

        NetObj.clients = self._players
        self.tryAddPlayer(self.owner)

    @property
    def playerCount(self):
        return len(self.players)

    def startGame(self):
        self.running = True
        asyncio.get_event_loop().create_task(self.startGameLoop())

    async def startGameLoop(self):
        lastTime = time.time()
        while self.running:
            if time.time() - lastTime < 1 / self.tickrate:
                asyncio.sleep(time.time() - lastTime)
            currentTime = time.time()
            self.gameLoop(currentTime - lastTime)
            lastTime = currentTime

    def gameLoop(self, deltatime: float):
        pass

    def close(self):
        self.running = False
        NetObj.clients = {}
        for player in self._players.values():
            player.send({'D': 0, 'P': 'gameclose', 'A': [], 'K': {}})

    def tryAddPlayer(self, client: 'GameClient') -> bool:
        if len(self._players) < self.maxPlayers:
            self._players[client.id] = client
            self.playerConnected(client)
            return True
        return False

    def removePlayer(self, client: 'GameClient'):
        client.send({'D': 0, 'P': 'gameleave', 'A': [], 'K': {}})
        self._players.pop(client.id, None)

    def playerConnected(self, client: 'GameClient'):
        NetObj.sendAllState(client.id)

    def playerDisconnected(self, client: 'GameClient'):
        pass

