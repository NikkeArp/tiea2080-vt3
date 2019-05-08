#!venv/bin/python
#-*- coding: utf-8 -*-
from vt3 import create_app
from flask import session, render_template
from flask.logging import create_logger

app = create_app()
logger = create_logger(app)

if __name__ == '__main__':
   app.run()