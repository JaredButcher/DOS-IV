import typing
import gamesite.gamebase.networkenums as netenums
import collections

class Lobby:
    lobbyCount = 0
    lobbies = []

    def __init__(self, router: 'network.GameServer', name: str, password: typing.Optional[str] = ''):
        self.players = {}
        self.password = password
        self.router = router
        self.name = name
        self.lobbyId = Lobby.lobbyCount
        lobbyCount =  (Lobby.lobbyCount + 1) % 2**31
        Lobby.lobbies.append(self)
        router.setHandler(netenums.CHANNEL.GAME, self.lobbyId, self.messageHandler)

    def messageHandler(self, message: 'network.Message'):
        '''Process messages addressed to the lobby
        '''
        pass

    def addPlayer(self, playerId: int, password: typing.Optional[str] = '') -> bool:
        '''Only call from network.GameClient
            Add a player to the lobby and send them the lobby info, returns if password was correct
        '''
        if self.password == password:
            self.players[playerId] = LobbyPlayer(playerId)
            #TODO send lobby info to player
            return True
        else:
            return False

    def removePlayer(self, playerId: int):
        '''Only call from network.GameClient
            Removes player from game, called by player if their connection closes
        '''
        self.players.pop(playerId)
        #TODO Send message?
        if len(self.players) == 0: self.close()

    def close(self):
        for player in self.players:

        self.router.removeHandler(netenums.CHANNEL.GAME, self.lobbyId)
        if self in Lobby.lobbies: Lobby.lobbies.remove(self)

class LobbyPlayer(collections.UserDict):
    def __init__(self, sessionId: int):
        self['sessionId'] = sessionId
        self['name'] = "Player"
