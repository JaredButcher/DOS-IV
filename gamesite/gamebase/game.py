import multiprocessing
from .taskProcess import TaskProcess
import time
import random

random.seed(time.time())

class Game(TaskProcess):

    gameIdCounter = random.getrandbits(32)

    def __init__(self, tickrate=30):
        '''Launches a child process to check network and run the game loop
        Args:
            tickrate (int): how many times per second to run event loop
        '''
        self.currentTime = time.time()
        self.netpipeParent, self.netpipeChild = multiprocessing.Pipe()
        self.tickrate = tickrate
        self.gameId = Game.gameIdCounter
        self.players = {}
        Game.gameIdCounter += 1
        super().__init__()

    def processStart(self):
        return GameChild(self.gameId, self.stopEvent, self.netpipeChild, self.tickrate).run()

    def getId(self):
        '''Get the unique id of this game
        '''
        return self.gameId

    def pollSendMessages(self):
        '''See if the child process has any messages in the pipe to send over the network and send them
        '''
        while self.netpipeParent.poll():
            message = self.netpipeParent.recv()
            self.players[message.user].send(message)

    def recvMessage(self, message):
        '''Pass network message to child process
        Args:
            message (Message): received message to send to child process
        '''
        self.netpipeParent.send(message)

    def addPlayer(self, player):
        '''Add a player to the lobby and send them the lobby info
        Args:
            client (GameClient): player to add
        '''
        self.players[client.clientId] = player
        player.setBelongsTo(self)

    def removePlayer(self, player):
        '''Removes player from game, called by player if their connection closes
        '''
        pass

class GameChild():
    def __init__(self, gameId, stopEvent, netPipe, tickrate):
        self.gameId = gameId
        self.stopEvent = stopEvent
        self.netpipeChild = netPipe
        self.tickrate = tickrate
        self.currentTime = time.time()

    def run(self):
        while not self.stopEvent.is_set():
            #Receive new network messages
            messages = []
            while self.netpipeChild.poll():
                messages.append(self.netpipeChild.recv())
            if len(messages) > 0:
                self.networkRec(messages)
            #Calculate elasped time
            pastTime = self.currentTime
            self.currentTime = time.time()
            #Delay to match tick rate
            time.sleep(max(0, pastTime - (self.currentTime - 1 / self.tickrate)))
            self.currentTime = time.time()
            #Run game loop
            self.gameLoop(self.currentTime - pastTime)
        return 0

    def gameLoop(self, deltatime):
        '''Override to create game loop, called in child process
        Args:
            deltatime (float): time in seconds sense it was called last
        '''
        pass

    def networkRec(self, messages):
        '''Override to process received messages, called in child process
        Args:
            messages ([Message]): list of messages received
        '''
        pass

    def processCommandMessage(self, message):
        '''See if the incoming message is a control message and process it accordingly
        Args:
            message (message): incoming message
        Returns:
            (bool): was it a command message, if so then don't pass it on farther
        '''
        if message.form == "":
            pass
        return False
