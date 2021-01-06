from gameserver.gameserver import GameServer
import argparse
import sys

def main(argv=None):
    parser = argparse.ArgumentParser(description="gameserver")
    parser.add_argument("port", type=int, help="Port to host server on")
    parser.add_argument("name", help="Name of server")
    parser.add_argument("webserver", nargs='?', default='http://localhost:5000', help="Server to send status updates to")
    parser.add_argument("password", nargs='?', type=str, default='', help="Server password")
    parser.add_argument("-l", type=int, default=20, help="Log level")
    parser.add_argument("-f", type=str, default='', help="Log file")
    args = parser.parse_args(argv if argv else sys.argv[1:])

    server = GameServer(args.port, args.webserver, args.name, password=args.password, logLevel=args.l, logFile=args.f)
    try:
        i = ''
        while i != 'q':
            i = input()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        print("Closing server, may take a minute")
        server.join(30)

if __name__ == '__main__':
    main("4647 Toaster")
