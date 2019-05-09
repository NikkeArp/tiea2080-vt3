#!venv/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

toolbar = DebugToolbarExtension()

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping({
            'SECRET_KEY': '\xb8o\x9f\x91\x07\x93{Z\x947\xc2s(\x9f',
            'PASS_W' : '50f84218b6f13d32fa6b4ae22d2f9688ec64c125cca9909a827453f98731e445df25754a480144d73105259e75082b159843ce8a3fd4d853693368c24216f726',
            'LOGPATH': 'logs/server.log',
            'ENV': 'developement',
            'JSONPATH': 'data/data.json',
            'DEBUG': True
        })
    if config:
        app.config.from_mapping(config)
    

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    with app.app_context():
        from . import user
        app.register_blueprint(user.user)

    toolbar.init_app(app)

    return app