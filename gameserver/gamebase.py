from gameserver.gameclient import GameClient
from gameserver.netobj import NetObj
from gameserver.player import Player
import time
import asyncio
import typing

class GameBase(NetObj):
    def __init__(self):
        self.gameName = "None"
        self.maxPlayers = 1
        self.tickrate = 20
        self.running = False
        self.players: typing.Dict[int, 'Player'] = {}
        super().__init__()

    @property
    def activePlayerCount(self):
        return len(self.activePlayers)

    @property
    def connectedPlayerCount(self):
        return len(self.connectedPlayers)

    @property
    def connectedPlayers(self):
        return {key:value for (key,value) in self.players.items() if value.connected}

    def setOwner(self, newOwner: 'Player'):
        for player in self.players.values():
            if player.owner and player != newOwner:
                player.setOwner(False)
        if not newOwner.owner: newOwner.setOwner(True)

    @NetObj.gameAllRpc
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
        for player in self.connectedPlayers.values():
            player.send({'D': 0, 'P': 'gameclose', 'A': []})

    def newPlayer(self, client: 'GameClient'):
        if self.maxPlayers >= self.connectedPlayerCount:
            self.players[client.id] = Player(client)
            client.onDisconnect = self.playerDisconnected
            NetObj.sendAllState(client.id)
            if self.connectedPlayerCount == 1:
                self.setOwner(self.players[client.id])
        else:
            client.close()

    def removePlayer(self, client: 'GameClient'):
        self.players.pop(client.id, None)
        client.send({'D': 0, 'P': 'gameleave', 'A': []})

    def playerConnected(self, client: 'GameClient'):
        self.newPlayer(client)

    def playerDisconnected(self, client: 'GameClient'):
        self.removePlayer(client)

    def serialize(self) -> dict:
        superSerial = super().serialize()
        superSerial['A'][1].update({'gameName': self.gameName, 'maxPlayers': self.maxPlayers, 'running': self.running, 'players': [player.id for player in self.players]})
        return superSerial

