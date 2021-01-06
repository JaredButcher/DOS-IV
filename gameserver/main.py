from gameserver.gameserver import GameServer
from gameserver.logging import initLogging
import argparse
import sys

def main(argv=None):
    parser = argparse.ArgumentParser(description="gameserver")
    parser.add_argument("port", type=int, help="Port to host server on")
    parser.add_argument("name", help="Name of server")
    parser.add_argument("webserver", nargs='?', default='http://localhost:5000', help="Server to send status updates to")
    parser.add_argument("maxGames", nargs='?', type=int, default=4, help="Max number of games to host")
    parser.add_argument("maxPlayers", nargs='?', type=int, default=12, help="Max number of players to host")
    parser.add_argument("password", nargs='?', type=str, default='', help="Server password")
    args = parser.parse_args(argv if argv else sys.argv[1:])

    initLogging(20)
    server = GameServer(args.port, args.webserver, args.name, args.maxGames, args.maxPlayers, args.password)
    server.start()

if __name__ == '__main__':
    main("4647 Toaster")
