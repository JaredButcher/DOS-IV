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
        Game.gameIdCounter += 1
        super().__init__()

    def processStart(self):
        '''Called on child process, runs in loop
        '''
        while not self.stop.is_set():
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

    def getId(self):
        '''Get the unique id of this game
        '''
        return self.gameId

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
    
