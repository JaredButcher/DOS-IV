from gameserver.gameserver import GameServer
from gameserver.logging import initLogging

def run():
    initLogging(10)
    server = GameServer(4247, 'http://localhost:5000', "Jim", 4, 20, 'jeb')
    try:
        server.run()
    finally:
        server.close()

if __name__ == '__main__':
    run()
