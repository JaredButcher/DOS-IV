from enum import IntEnum

class Channels(IntEnum):
    SERVER = 0
    PROCESS = 1
    LOBBY = 2
    GAME = 3
    CLIENT = 4
    CLIENT_GAME = 5

class CLIENT_CHANNEL(IntEnum):
    CLIENT = 0
    GAME = 1

class ServerForms(IntEnum):
    REGISTER = 0

class InClientForms(IntEnum):
    SET_USERNAME = 0

class OutClientForms(IntEnum):
    USERNAME = 0
    LOBBY = 1