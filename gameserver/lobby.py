from gameserver.process import Process
from gameserver.message import Message
import gameserver.serverenums as serverenums
from multiprocessing import Queue
import time
import typing
from enum import IntEnum

class LobbyForms(IntEnum):
    PLAYER_JOIN = 0
    PLAYER_LEAVE = 1
    PLAYER_DISCONNECT = 2
    PLAYER_CONNECT = 3

class Lobby(Process):
    def __init__(self, outQueue: 'Queue', lobbyId: int, name: str, owner: str, password: typing.Optional[str] = ''):
        self.password = password
        self.name = name
        self.owner = owner
        self.id = lobbyId
        self.game = None
        self.tickRate = 0
        super().__init__(outQueue, name=f'Lobby{self.id}')

    def run(self):
        self.players = {}
        self.maxPlayers = 1
        lastTime = time.time()
        while not self.stopEvent.is_set():
            currTime = time.time()
            if self.tickRate > 0 and currTime - lastTime > 1 / self.tickRate:
                self.gameLoop(currTime - lastTime)
                lastTime = currTime
            while self.inQueue.not_empty():
                message = self.inQueue.get()
                if message['C'] == serverenums.Channels.LOBBY.value:
                    self.lobbyHandle(message)
                elif message['C'] == serverenums.Channels.GAME.value:
                    self.gameHandle(message)
        self.close()

    def gameLoop(self, deltatime):
        '''Override in child class'''
        pass

    def gameHandle(self, message: 'Message'):
        '''Override in child, Process messages addressed to the game
        '''
        pass

    def lobbyHandle(self, message: 'Message'):
        '''Process messages addressed to the lobby
        '''
        if message['F'] == LobbyForms.PLAYER_JOIN.value:
            pass
        elif message['F'] == LobbyForms.PLAYER_LEAVE.value:
            pass
        elif message['F'] == LobbyForms.PLAYER_DISCONNECT.value:
            pass
        elif message['F'] == LobbyForms.PLAYER_CONNECT.value:
            pass

    def close(self):
        for player in self.players.keys:
            self.outQueue.put(Message({'C': serverenums.Channels.CLIENT.value, 'F': serverenums.OutClientForms.LOBBY.value, 'SID': player, 'ID': 0, 'MSG': 'Lobby Closed'}))
