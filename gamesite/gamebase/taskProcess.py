import multiprocessing
import asyncio
import time

class TaskProcess(multiprocessing.Process):
    '''Just a auto starting daemon process with a stop command and stop event
    '''
    def __init__(self, networkQueue: 'multiprocessing.Queue', **kwargs):
        super().__init__(daemon=True, **kwargs)
        self.networkQueue = networkQueue
        self.queue = multiprocessing.Queue()
        self.stopEvent = multiprocessing.Event()
        
    def stop(self):
        '''Stops the child process
        '''
        self.stopEvent.set()
    
