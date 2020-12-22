import typing
import gamesite.gamebase.network as network

class Lobby():
    lobbyCount = 0

    def __init__(self, router: 'network.GameServer', password: typing.Optional[str] = ''):
        self.players = []
        self.password = password
        self.router = router
        self.lobbyId = lobbyCount
        lobbyCount =  (lobbyCount + 1) % 2**31
        router.setHandler(network.CHANNEL.GAME, self.lobbyId, self.messageHandler)

    def messageHandler(self, message: 'network.Message'):
        '''Process messages addressed to the lobby
        '''
        pass

    def addPlayer(self, playerId: int, password: typing.Optional[str] = '') -> bool:
        '''Only call from network.GameClient
            Add a player to the lobby and send them the lobby info, returns if password was correct
        '''
        if self.password == password:
            self.players.append(playerId)
            #TODO send lobby info to player
            return True
        else:
            return False

    def removePlayer(self, playerId: int):
        '''Only call from network.GameClient
            Removes player from game, called by player if their connection closes
        '''
        if playerId in self.players: 
            self.players.remove(playerId)
            #TODO Send message?
        if len(self.players) == 0: self.close()

    def close(self):
        #TODO Send messages to remaining palyers?
        self.router.removeHandler(network.CHANNEL.GAME, self.lobbyId)
