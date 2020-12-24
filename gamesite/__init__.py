from flask import Flask
import os

def createApp(config="gamesite.config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config)
    if 'GAMESITE_CONFIG' in os.environ:
        app.config.from_envvar('GAMESITE_CONFIG')

    if not 'secretSessionKey' in app.config:
        app.secret_key = b'development'

    from gamesite.model import db
    db.init_app(app)

    return app