import typing
import gamesite.gamebase.networkenums as netenums
from gamesite.gamebase.message import Message
import collections

class Lobby:
    lobbyCount = 0

    def __init__(self, router: 'gamesite.gamebase.network.GameServer', name: str, password: typing.Optional[str] = ''):
        self.players = {}
        self.password = password
        self.router = router
        self.name = name
        self.lobbyId = Lobby.lobbyCount
        lobbyCount =  (Lobby.lobbyCount + 1) % 2**31

    @property
    def id(self):
        return self.lobbyId

    def handle(self, message: 'Message'):
        '''Process messages addressed to the lobby
        '''
        pass

    def addPlayer(self, player: 'gamesite.gamebase.network.GameClient', password: typing.Optional[str] = '') -> bool:
        '''Only call from network.GameClient
            Add a player to the lobby and send them the lobby info, returns if password was correct
        '''
        if self.password == password:
            self.players[player.id] = player
            #TODO send lobby info to player
            return True
        else:
            return False

    def rmPlayer(self, playerId: int):
        '''Only call from network.GameClient
            Removes player from game, called by player if their connection closes
        '''
        self.players.pop(playerId)
        #TODO Send message?
        if len(self.players) == 0: self.close()

    def close(self):
        for player in self.players.values:
            player.setLobby(None)
