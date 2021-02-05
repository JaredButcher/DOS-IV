import logging
from gameserver.gameclient import GameClient
from gameserver.player import Player
from gameserver.netobj import NetObj
import time
import asyncio
import typing

class GameBase(NetObj):
    def __init__(self, prevGame: typing.Optional['GameBase'] = None):
        super().__init__(0, 0)
        self.gameName = prevGame.gameName if prevGame else "None"
        self.maxPlayers = prevGame.maxPlayers if prevGame else 1
        self.owner = None
        self.tickrate = 20
        self.running = False
        self.players: typing.Dict[int, 'Player'] = {}
        if prevGame:
            self.newPlayer(prevGame.owner.client)
            for player in prevGame.players:
                self.newPlayer(player.client)

    @property
    def playerCount(self):
        return len(self.players)

    @property
    def connectedPlayerCount(self):
        return len(self.connectedPlayers)

    @property
    def connectedPlayers(self):
        return [player for player in self.players.values() if player.client.connected]

    def setOwner(self, newOwner: 'Player'):
        self.rpcAll("setOwner", newOwner.id)
        self.owner = newOwner

    def startGame(self):
        self.running = True
        self.rpcAll("startGame")
        asyncio.get_event_loop().create_task(self._startGameLoop())

    async def _startGameLoop(self):
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
        self.rpcAll("__close__", "Game closed")

    def newPlayer(self, client: 'GameClient'):
        if client not in [player.client for player in self.players.values()]:
            if self.maxPlayers >= self.connectedPlayerCount:
                logging.log(30, "New Player " + str(self.connectedPlayerCount))
                self.players[client.id] = Player(client, self)
                client.onDisconnect = self.playerDisconnected
                if self.connectedPlayerCount == 1:
                    self.setOwner(self.players[client.id])
            else:
                client.close()

    def removePlayer(self, client: 'GameClient'):
        self.players.pop(client.id, None)
        self.rpcTarget(client, "__close__", "Player Removed")
        self.rpcTarget()

    def playerConnected(self, client: 'GameClient'):
        self.newPlayer(client)

    def playerDisconnected(self, client: 'GameClient'):
        logging.log(30, "Player disconnected " + str(client.id))
        self.removePlayer(client)

    def serialize(self, **kwargs) -> dict:
        return super().serialize(gameName = self.gameName, maxPlayers = self.maxPlayers, running = self.running, players = [player.id for player in self.players.values()], **kwargs)

