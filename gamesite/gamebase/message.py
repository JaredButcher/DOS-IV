import collections
import json

class Message(collections.UserDict):
    '''Universal form for messages, used to pack and unpack messages
    '''
    @staticmethod
    def parseMessage(message):
        '''Parse received json string into message object
        '''
        return Message(**(json.loads(message)))

    def __init__(self, src: int, des: int, channel: int, form: int, content: Optional[dict] = {}):
        '''Create a new message
        Args:
            src (int): source
            des (int): destination
            channel (int): channel
            form (int): type of message
            content (object): any message content
        '''
        super().__init__({'src': src, 'des': des, 'channel': channel, 'form': form, 'content': content})

    def __str__(self):
        return json.dumps(self)

    def toString(self):
        '''Packs message into sendable string
        '''
        return str(self)
