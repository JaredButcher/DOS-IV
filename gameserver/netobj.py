import typing

class NetObj:
    netObjs = {}
    rootObjs = {}
    send = None
    netIdCounter = 1

    @staticmethod
    def find(name: str) -> typing.Union['NetObj', None]:
        path = name.split('/')
        obj = NetObj.rootObjs.get(path[0], None)
        for entry in path[1:]:
            if obj:
                obj = obj.children.get(entry, None)
            else:
                return None
        return obj

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
        self.type = type(self).__name__
        self.name = name if name else self.type + str(self.id)
        self.children = {}
        self._cmds = {}
        for attrName in dir(self):
            attr = getattr(self, attrName)
            if callable(attr) and attrName[0:3] == 'cmd':
                self._cmds[attrName] = attr

    @property
    def id(self):
        return self._id

    def onStart(self):
        '''Ran on game start, override
        '''
        pass

    def onUpdate(self, deltatime: float):
        '''Ran on each clock cycle, override
        '''
        pass

    def findChild(self, name: str) -> typing.Union['NetObj', None]:
        path = name.split('/')
        obj = self.children.get(path[0], None)
        for entry in path[1:]:
            if obj:
                obj = obj.children.get(entry, None)
            else:
                return None
        return obj

    def attachChild(self, child: 'NetObj'):
        NetObj.rootObjs.pop(child.name, None)
        if child.parent:
            child.parent.children.pop(child.name, None)
        child.parent = self
        self.children[child.name] = child

    def rpcAll(self, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]})

    def rpcTarget(self, clientId: int, procedure: str, *args):
        NetObj.send({'D': self.id, 'P': procedure, 'A': [*args]}, clientId)

    def recvCommand(self, commandMsg: dict, isOwner: bool):
        print(self.id)
        if self.authority == commandMsg['S'] or self.authority is None and isOwner:
            cmd = self._cmds.get(commandMsg['P'], None)
            print(cmd)
            print(self._cmds)
            if cmd: cmd(*commandMsg['A'])

    def serialize(self, **kwargs) -> dict:
        return {'D': 0, 'P': '__init__', 'A': [self.type, 
            {'id': self.id, 'name': self.name, 'parent': self.parent.id if self.parent else None, 'authority': self.authority, 
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
        for child in self.children.values():
            child._destory()
        self.children = None
        