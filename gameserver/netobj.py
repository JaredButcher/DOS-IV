import typing

class NetObj:
    idCounter = 1
    netObjs = {}
    clientRpcs = {}
    clients = {}

    @staticmethod
    def clientRpc(cls: str):
        '''Remote procedure call from client
        '''
        def inner(funct):
            classRpcs = NetObj.clientRpcs.get(cls, {})
            classRpcs[funct.__name__] = funct
            NetObj.clientRpcs[cls] = classRpcs
            return funct
        return inner

    @staticmethod
    def gameAllRpc(funct):
        '''Remote procedure call from server to all clients
        '''
        def inner(self, *args):
            for client in NetObj.clients.values():
                client.send({'D': self.id, 'P': funct.__name__, 'A': args})
            funct(self, *args)
        return inner

    @staticmethod
    def gameSelectRpc(funct):
        '''Remote procedure call from server to a select client
        '''
        def inner(self, target: int, *args):
            client = NetObj.clients.get(target, None)
            if client:
                client.send({'D': self.id, 'P': funct.__name__, 'A': args})
            funct(self, target, *args)
        return inner

    @staticmethod
    def handleClientRpc(message: dict):
        netObj = NetObj.netObjs.get(message['D'], None)
        if netObj and (netObj.authority is None or netObj.authority == message['S']):
            rpc = NetObj.clientRpcs.get(netObj.type, {}).get(message['P'], None)
            if rpc:
                rpc(netObj, *(message['A']))

    @staticmethod
    def sendAllState(clientId: int):
        client = NetObj.clients.get(clientId, None)
        if client:
            for netObj in NetObj.netObjs.values():
                client.send(netObj)

    def __init__(self, authority: typing.Optional[int] = 0):
        self.authority = authority
        self.type = type(self).__name__
        self._id = NetObj.idCounter
        NetObj.idCounter += 1
        NetObj.netObjs[self.id] = self
        serialObj = self.serialize()
        for client in NetObj.clients.values():
                client.send(serialObj)

    def destroy(self):
        NetObj.netObjs.pop(self.id, None)
        for client in NetObj.clients.values():
            client.send({'D': self.id, 'P': '__del__', 'A': [], 'K': {}})

    def serialize(self) -> dict:
        return {'D': 0, 'P': '__init__', 'A': [self.type, {'id': self.id, 'authority': self.authority}]}

    @property
    def id(self):
        return self._id
