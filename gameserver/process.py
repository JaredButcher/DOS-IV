import multiprocessing
import time
from enum import IntEnum
from gameserver.serverenums import Channels
from gameserver.message import Message

STOP_WAIT = .3

class IPCForms(IntEnum):
    LOG = 0
    STOP = 1

class Process(multiprocessing.Process):
    '''An auto starting daemon process with a stop command, ipc logging, and io queues
    '''
    def __init__(self, outQueue: 'multiprocessing.Queue', **kwargs):
        super().__init__(daemon=True, **kwargs)
        self.outQueue = outQueue
        self.inQueue = multiprocessing.Queue()
        self.stopEvent = multiprocessing.Event()
        self.start()

    def put(self, message):
        self.inQueue.put(message)

    def log(self, level: int, message: str):
        #TODO: Fix log
        self.outQueue.put(Message({'C': Channels.SERVER.value, 'F': IPCForms.LOG.value, 'LEVEL': level, 'MSG': message}))

    def stop(self):
        '''Stops the child process
        '''
        self.stopEvent.set()
        self.join(STOP_WAIT)
        if self.is_alive():
            self.log(30, f'Process {self.name} did not shutdown quietly')
            self.terminate()

    
