import collections
import json
import typing

class Message(collections.UserDict):
    '''Universal form for messages, used to pack and unpack messages
    '''
    @staticmethod
    def parseMessage(message):
        '''Parse received json string into message object
        '''
        try:
            return Message(data = json.loads(message))
        except json.JSONDecodeError:
            return None

    def __init__(self, src: int, des: int, channel: int, form: int, content: typing.Optional[dict] = {}, data: typing.Optional[dict] = None):
        '''Create a new message
        Args:
            src (int): source
            des (int): destination
            channel (int): channel
            form (int): type of message
            content (object): any message content
        '''
        if data:
            super().__init__(data)
        else:
            super().__init__({'src': src, 'des': des, 'channel': channel, 'form': form, 'content': content})

    def __str__(self):
        return json.dumps(self)

    def toString(self):
        '''Packs message into sendable string
        '''
        return str(self)

    def matches(self, channel: typing.Optional[str] = None, des: typing.Optional[str] = None, form: typing.Optional[str] = None) -> bool:
        return (not channel or self['channel'] == channel) and (not des or self['des'] == des) and (not form or self['form'] == form)
