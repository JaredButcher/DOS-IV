from gameserver.netobj import NetObj
from gameserver.gameclient import GameClient
import logging


class Player(NetObj):
    '''A NetObj adapter to the GameClient
    '''
    def __init__(self, client: GameClient):
        self.client = client
        super().__init__(client.id)

    @property
    def id(self):
        return self.client.id

    @property
    def username(self) -> str:
        return self.client.username

    @NetObj.gameAllRpc
    def setUsername(self, username: str):
        self.client.username = username

    @property
    def owner(self) -> bool:
        return self.client.owner

    @NetObj.gameAllRpc
    def setOwner(self, isOwner: bool):
        self.client.owner = isOwner

    @property
    def connected(self) -> bool:
        return self.client.connected

    def send(self, msg: dict):
        self.client.send(msg)
    
    def serialize(self) -> dict:
        superSerial = super().serialize()
        superSerial['A'][1].update({'id': self.id, 'username': self.username, 'owner': self.owner})
        return superSerial