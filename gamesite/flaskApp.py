from gamesite import createApp
import flask
from gamesite.gamebase.network import GameServer

app = createApp()
gameServer = GameServer(4247)

@app.route('/')
def home():
    if 'ahh' not in flask.session: flask.session['ahh'] = 0
    flask.session['ahh'] += 1
    print(flask.session['ahh'])
    return flask.render_template('home.html')

def run():
    app.run()

if __name__ == '__main__':
    run()
