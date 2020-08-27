from gamesite import createApp
import flask
from gamesite.gamebase.network import GameServer

app = createApp()
gameServer = GameServer(4247)

@app.route('/')
def home():
    return flask.render_template('home.html')

if __name__ == '__main__':
    app.run()
