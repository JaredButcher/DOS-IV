from enum import IntEnum

class CHANNEL(IntEnum):
    SERVER = 0
    CLIENT = 1
    LOBBY = 2

class SERVER_HANDLERS(IntEnum):
    NETWORK = 0

class NETWORK_FORMS(IntEnum):
    REGISTER = 0