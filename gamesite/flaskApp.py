from gamesite import createApp
from gamesite.serverinfo import ServerInfo
import flask
import random
import time



app = createApp()

@app.route('/')
def home():
    return flask.render_template('home.html', servers = ServerInfo.getServers())

@app.route('/server/register', methods=['POST'])
def registerServer():
    newId = ServerInfo.createServerInfo(flask.request.get_json(), flask.request.remote_addr)
    if newId:
        return flask.make_response(flask.jsonify({'sucess': True, 'id': newId})), 201
    else:
        return flask.make_response(flask.jsonify({'error': 'Invalid request'})), 400

@app.route('/server/<int:server_id>/update', methods=['POST'])
def serverUpdate(server_id):
    if ServerInfo.updateServer(server_id, flask.request.get_json(), flask.request.remote_addr):
        return flask.make_response(flask.jsonify({'sucess': True})), 200
    else:
        return flask.make_response(flask.jsonify({'error': 'Invalid request'})), 400

@app.route('/server/get', methods=['POST'])
def serverGet(server_id):
    return flask.make_response(flask.jsonify({'sucess': True, 'servers': ServerInfo.getServers()})), 200

def run():
    app.run()

if __name__ == '__main__':
    run()
