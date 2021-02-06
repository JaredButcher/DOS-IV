import typing

class NetObj:
    netObjs = {}
    rootObjs = {}
    send = None
    netIdCounter = 1

    @staticmethod
    def find(name: str) -> typing.Union[NetObj, None]:
        delimiter = name.find('/')
        if delimiter:
            objName = name[0:delimiter]
            path = name[name.find('/') + 1:delimiter]
            obj = NetObj.rootObjs.get(objName, None)
            if obj:
                return obj.findChild(path)
        else:
            return NetObj.rootObjs.get(name, None)

    @staticmethod
    def attachRootObj(obj: 'NetObj'):
        if obj.parent:
            obj.parent.children.pop(obj.name, None)
        obj.parent = None
        NetObj.rootObjs[obj.name] = obj

    def __init__(self, name: str = '', authority: typing.Optional[int] = None):
        self.authority = authority
        self._id = NetObj.netIdCounter
        NetObj.netIdCounter += 1
        NetObj.netObjs[self.id] = self
        self.parent = None
        self.name = name if name else str(type(self)) + str(self.id)
        self.children = {}
        self._cmds = {}
        for attrName in dir(self):
            attr = getattr(self, attrName)
            if callable(attr) and attrName[0:2] == 'cmd':
                self._cmds[attrName] = attr

    @property
    def id(self):
        return self._id

    def onStart(self):
        pass

    def onUpdate(self):
        pass

    def findChild(self, name: str) -> typing.Union[NetObj, None]:
        delimiter = name.find('/')
        if delimiter:
            objName = name[0:delimiter]
            path = name[name.find('/') + 1:delimiter]
            obj = self.children.get(objName, None)
            if obj:
                return obj.findChild(path)
        else:
            return self.children.get(name, None)

    def attachChild(self, child: 'NetObj'):
        NetObj.rootObjs.pop(child.name, None)
        if obj.parent:
            obj.parent.children.pop(obj.name, None)
        obj.parent = self
        self.children[obj.name] = obj

    def rpcAll(self, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]})

    def rpcTarget(self, clientId: int, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]}, clientId)

    def recvCommand(self, commandMsg: dict):
        if self.authority == commandMsg['S']:
            cmd = self._cmds.get(commandMsg['P'], None)
            if cmd: cmd(*commandMsg['A'])

    def serialize(self, **kwargs) -> dict:
        return {'D': 0, 'P': '__init__', 'A': [self.type, 
            {'id': self.id, 'name': self.name, 'parent': self.parent.id, 'authority': self.authority, 
            'children': [child.id for child in self.children], **kwargs}]}

    def destroy(self):
        if self.parent:
           self.parent.children.pop(self.name, None)
        else:
            NetObj.rootObjs.pop(self.name, None)
        self._destory() 
        self.rpcAll('__del__')

    def _destory(self):
        NetObj.netObjs.pop(self.id, None)
        objectsToRemove = []
        for child in self.children.values():
            child._delete()
        self.children = None
        