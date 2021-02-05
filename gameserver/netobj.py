import typing

class NetObj:
    netObjs = {}
    send = None
    netIdCounter = 1

    def __init__(self, parent: typing.Optional[int] = 0, authority: typing.Optional[int] = 0):
        self.authority = authority
        self._id = NetObj.netIdCounter
        self.parent = parent
        NetObj.netIdCounter += 1
        NetObj.netObjs[self.id] = self
        self._cmds = {}
        for attrName in dir(self):
            attr = getattr(self, attrName)
            if callable(attr) and attrName[0:2] == 'cmd':
                self._cmds[attrName] = attr

    @property
    def id(self):
        return self._id

    def rpcAll(self, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]})

    def rpcTarget(self, clientId: int, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]}, clientId)

    def recvCommand(self, commandMsg: dict):
        if self.authority == commandMsg['S']:
            cmd = self._cmds.get(commandMsg['P'], None)
            if cmd: cmd(*commandMsg['A'])

    def serialize(self, **kwargs) -> dict:
        return {'D': 0, 'P': '__init__', 'A': [self.type, {'id': self.id, 'parent': self.parent, 'authority': self.authority, **kwargs}]}

    def destroy(self):
        NetObj.netObjs.pop(self.id, None)
        objectsToRemove = []
        for key, obj in NetObj.netObjs.items():
            if obj.parent == self.id:
                objectsToRemove.append(obj)
        for obj in objectsToRemove:
            obj.destory()
        self.rpcAll('__del__')