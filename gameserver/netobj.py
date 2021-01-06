import typing
import threading
import enum

class TARGET(enum.IntEnum):
    SERVER: 0
    CLIENT: 1
    ALL_CLIENTS: 2

class NetObj:
    idCounter = 1
    netObjLock = threading.Lock()
    netObjs = {}
    clientRpcs = {}
    sendMethod = None

    @staticmethod
    def setup(sendMethod: typing.Callable[['TARGET', dict, typing.Optional[int]], None]):
        NetObj.sendMethod = sendMethod

    @staticmethod
    def clientRpc(cls: str):
        '''Remote procedure call from client
        '''
        def inner(funct):
            classRpcs = NetObj.clientRpcs.get(cls, {})
            classRpcs[funct.__name__] = funct
            NetObj.clientRpcs[cls] = classRpcs
            def innerer(*args, **kwargs):
                funct(*args, **kwargs)
            return innerer
        return inner

    @staticmethod
    def gameAllRpc(funct):
        '''Remote procedure call from server to all clients
        '''
        def inner(self, *args, **kwargs):
            NetObj.sendMethod(TARGET.ALL_CLIENTS, {'D': self.id, 'P': funct.__name__, 'A': args, 'K': kwargs})
            funct(self, *args, **kwargs)
        return inner

    @staticmethod
    def gameSelectRpc(funct):
        '''Remote procedure call from server to a select client
        '''
        def inner(self, target: int, *args, **kwargs):
            NetObj.sendMethod(TARGET.CLIENT, {'D': self.id, 'P': funct.__name__, 'A': args, 'K': kwargs}, target)
            funct(self, target, *args, **kwargs)
        return inner

    @staticmethod
    def gameServerRpc(funct):
        '''Remote procedure call from game to server
        '''
        def inner(self, target: int, *args, **kwargs):
            NetObj.sendMethod(TARGET.SERVER, {'D': self.id, 'P': funct.__name__, 'A': args, 'K': kwargs})
            funct(self, target, *args, **kwargs)
        return inner

    @staticmethod
    def handleClientRpc(message: dict):
        netObj = NetObj.netObjs.get(message['D'], None)
        if netObj and (netObj.authority is None or netObj.authority == message['S']):
            rpc = NetObj.clientRpcs.get(netObj.type, {}).get(message['P'], None)
            if rpc:
                rpc(netObj, *(message['A']), **(message['K']))

    @classmethod
    def remoteConstruct(cls, *args, **kwargs):
        '''Make a netobject both here on the server and on the clients
        '''
        newNetObj = cls(*args, **kwargs)
        NetObj.sendMethod(TARGET.ALL_CLIENTS, {'D': newNetObj.id, 'P': '__init__', 'A': args, 'K': kwargs})
        return newNetObj

    def __init__(self, authority: typing.Optional[int] = None):
        self.authority = authority
        self.type = type(self).__name__
        with NetObj.netObjLock:
            self._id = NetObj.idCounter
            NetObj.idCounter += 1
            NetObj.netObjs[self.id] = self

    def __del__(self):
        with NetObj.netObjLock:
            NetObj.netObjs.pop(self.id, None)

    @property
    def id(self):
        return self._id
