from flask import Flask

def createApp(config="gamesite.config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_envvar('GAMESITE_CONFIG')

    from gamesite.model import db
    db.init_app(app)

    return app