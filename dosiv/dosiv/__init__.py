from flask import Flask

def createApp(config="dosiv.config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_envvar('DOSIV_CONFIG')

    from dosiv.model import db
    db.init_app(app)

    return app