from flask import Flask

def create_app(config="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config)
    from .database import db
    # db.init_app(app)
    return app