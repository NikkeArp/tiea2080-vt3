#!venv/bin/python
# -*- coding: utf-8 -*-

from flask import Flask

def create_app(config):
    app = Flask(__name__)
    app.config.from_mapping({
            'SECRET_KEY': '\xb8o\x9f\x91\x07\x93{Z\x947\xc2s(\x9f',
            'LOGPATH': 'logs/server.log',
            'JSONPATH': 'data/data.json',
            'DEBUG': True
        })

    if config:
        app.config.from_mapping(config)

    return app