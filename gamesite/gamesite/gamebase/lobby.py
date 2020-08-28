
class Lobby():
    def __init__(self):
        self.players = {}

    def recvMessage(self, message):
        '''Process messages addressed to the lobby
        Args:
            message (Message): the received network message
        '''
        pass

    def addPlayer(self, player):
        '''Add a player to the lobby and send them the lobby info
        Args:
            player (GameClient): player to add
        '''
        self.players[client.clientId] = player
        player.setBelongsTo(self)
        #TODO send lobby info to player

    def removePlayer(self, player):
        '''Removes player from game, called by player if their connection closes
        '''
        player.setBelongsTo(None)
        del self.players[player.clientId()]
