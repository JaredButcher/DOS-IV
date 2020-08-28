import multiprocessing
import asyncio
import time

class TaskProcess(multiprocessing.Process):
    '''Just a auto starting process with a stop command and stop event
    '''
    def __init__(self):
        super().__init__(target=self.processStart)
        self.stopEvent = multiprocessing.Event()
        self.start()

    def processStart(self):
        '''Override, this called in the child needs to check the stop event and stop
        '''
        return 0
        
    def stop(self):
        '''Stops the child process
        '''
        self.stopEvent.set()
    
