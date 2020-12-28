import json
import collections
import typing

class Message(collections.UserDict):
    @classmethod
    def parseMessage(data: str) -> typing.Optional['Message']:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return None
        if 'C' in data and 'F' in data:
            return Message(data)
        else:
            return None

    def contains(self, keys: typing.Sequence[str]) -> bool:
        for key in keys:
            if key not in self.data:
                return False
        return True

    def __str__(self):
        return json.dumps(self.data)

