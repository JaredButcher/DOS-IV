from gameserver.gameclient import GameClient
from gameserver.netobj import NetObj
import time
import asyncio
import typing

class GameBase(NetObj):
    def __init__(self, clients: typing.Dict[int, 'GameClient']):
        self.gameName = "None"
        self.maxPlayers = 1
        self.tickrate = 20
        self.running = False
        self.clients = clients
        super().__init__()

    @property
    def activePlayerCount(self):
        return len(self.activePlayers)

    @property
    def connectedPlayerCount(self):
        return len(self.connectedPlayers)

    @property
    def connectedPlayers(self):
        return {key:value for (key,value) in self.clients.items() if value.connected}

    @property
    def activePlayers(self):
        return {key:value for (key,value) in self.clients.items() if value.get('active', False)}

    def resetPlayerData(self):
        '''Removes all dictionary values of the clients except for owner status
        '''
        for client in self.clients.values():
            if client.get('owner', False):
                client.data = {'owner': True}
            else:
                client.data = {}
    
    def removePlayerAttr(self, key: str):
        for client in self.clients.values():
            client.pop(key, None)

    @NetObj.gameAllRpc
    def setOwner(self, clientId: int):
        self.removePlayerAttr('owner')
        self.clients.get(clientId, {})['owner'] = True

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
            client['active'] = True
            NetObj.sendAllState(client.id)
            if self.connectedPlayerCount == 1:
                self.setOwner(client.id)
        else:
            client.close()

    def removePlayer(self, client: 'GameClient'):
        client['active'] = False
        client.send({'D': 0, 'P': 'gameleave', 'A': []})

    def playerConnected(self, client: 'GameClient'):
        self.newPlayer(client)

    def playerDisconnected(self, client: 'GameClient'):
        self.removePlayer(client)

    def serialize(self) -> dict:
        superSerial = super().serialize()
        superSerial['A'][1].update({'gameName': self.gameName, 'maxPlayers': self.maxPlayers, 'running': self.running, 'clients': {player.id:{} for player in self.activePlayers.values()}})
        return superSerial

