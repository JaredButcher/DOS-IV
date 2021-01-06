from gameserver.netobj import NetObj
from gameserver.gamebase import GameBase
import multiprocessing
import functools
import typing

class GameIntr:
    gameCount = 1

    def __init__(self, netQueue: 'multiprocessing.Queue', game: 'GameBase', owner: int, password: typing.Optional(str) = ''):
        super().__init__()
        self.players = []
        self._id = GameIntr.gameCount
        GameIntr.gameCount += 1
        self.gameQueue = multiprocessing.Queue()
        self.gameProcess = multiprocessing.Process(target=functools.partial(game, self.id, netQueue, self.gameQueue, owner, password), daemon=True)
        self.gameProcess.start()

    def id(self):
        return self._id

    def send(self, message: dict):
        self.gameQueue.put(message)

