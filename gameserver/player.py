from gameserver.gameclient import GameClient
from gameserver.netobj import NetObj
import logging


class Player(NetObj):
    '''A NetObj adapter to the GameClient
    '''
    def __init__(self, client: GameClient, **kwargs):
        self.client = client
        super().__init__(authority=client.id, **kwargs)

    @property
    def clientId(self):
        return self.client.id

    @property
    def username(self) -> str:
        return self.client.username

    @property
    def owner(self) -> bool:
        return self.client.owner

    @property
    def connected(self) -> bool:
        return self.client.connected

    def rpcSetUsername(self, username: str):
        self.client.username = username
        self.rpcAll("rpcSetUsername", username)

    def cmdSetUsername(self, username: str):
        print("SET USERNAME CMD")
        self.rpcSetUsername(username)

    def rpcSetOwner(self, isOwner: bool):
        self.client.owner = isOwner
        self.rpcAll("rpcSetOwner", isOwner)

    def cmdSetOwner(self, isOwner: bool):
        self.rpcSetOwner(isOwner)

    def send(self, msg: dict):
        self.client.send(msg)
    
    def serialize(self) -> dict:
        return super().serialize(clientId = self.clientId, username = self.username, owner = self.owner)