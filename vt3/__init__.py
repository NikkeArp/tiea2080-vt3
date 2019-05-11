#!venv/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

toolbar = DebugToolbarExtension()

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping({
            'SECRET_KEY': '\xb8o\x9f\x91\x07\x93{Z\x947\xc2s(\x9f',
            'PASS_W' : '50f84218b6f13d32fa6b4ae22d2f9688ec64c125cca9909a827453f98731e445df25754a480144d73105259e75082b159843ce8a3fd4d853693368c24216f726',
            'ADMIN_PASS_W':'6c9ab998588d2b66c2aac937482d2a22a7edf4311689787a001319178136f82b451c487e85ff07f2d054d1244d1b931d42e30e3b0deea2a05c283b845925d5bd',
            'LOGPATH': 'logs/server.log',
            'ENV': 'developement',
            'JSONPATH': 'data/data.json',
            'DEBUG_TB_INTERCEPT_REDIRECTS': False,
            'DEBUG': True
        })
    if config:
        app.config.from_mapping(config)
    

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    with app.app_context():
        from . import user
        app.register_blueprint(user.user)
        from . import admin
        app.register_blueprint(admin.admin)

    toolbar.init_app(app)

    @app.route('/json-error')
    def json_error():
        '''JSON-error page to inform user about JSON-error.'''
        return render_template('JSON_e.html')

    return app