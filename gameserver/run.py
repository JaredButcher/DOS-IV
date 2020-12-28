from gameserver.gameserver import GameServer
from gameserver.logging import initLogging

def run():
    initLogging(10)
    server = GameServer(4247)
    try:
        server.run()
    finally:
        server.close()

if __name__ == '__main__':
    run()
