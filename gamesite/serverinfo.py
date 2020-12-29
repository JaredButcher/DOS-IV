import random
import time
import typing

SERVER_TIMEOUT = 60

random.seed()

def checkDictFormat(original: dict, format: dict) -> bool:
    for key, value in format.items():
        if type(original.get(key, None)) != value:
            return False
    return True

class ServerInfo:
    _servers = {}

    def __init__(self, name: str, address: str, port: int, maxGames: int, maxPlayers: int, **kwargs):
        self.name = name
        self.address = address
        self.port = port
        self.maxGames = maxGames
        self.maxPlayers = maxPlayers
        self.currentGames = 0
        self.currentPlayers = 0
        self.lastUpdate = time.time()
        while True:
            self.id = random.getrandbits(32)
            if self.id not in ServerInfo._servers: break
        ServerInfo._servers[self.id] = self

    @staticmethod
    def updateServer(id: int, update: dict, address: str) -> bool:
        server = ServerInfo._servers.get(id, None)
        if server and server.address == address and checkDictFormat(update, {'currentGames': int, 'currentPlayers': int}):
            server.lastUpdate = time.time()
            server.currentGames = update['currentGames']
            server.currentPlayers = update['currentPlayers']
            return True
        else:
            return False

    @staticmethod
    def createServerInfo(request: dict, address: str) -> typing.Optional[int]:
        if checkDictFormat(request, {'name': str, 'port': int, 'maxGames': int, 'maxPlayers': int}):
            newServerInfo = ServerInfo(address=address, **request)
            return newServerInfo.id

    @staticmethod
    def getServers() -> typing.List['ServerInfo']:
        validServers = {}
        currentTime = time.time()
        for key, value in ServerInfo._servers.items():
            if value.lastUpdate - currentTime < SERVER_TIMEOUT:
                validServers[key] = value
        ServerInfo._servers = validServers
        return ServerInfo._servers.values()
         