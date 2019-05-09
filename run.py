#!venv/bin/python
#-*- coding: utf-8 -*-
from vt3 import create_app
from flask import session, render_template

app = create_app()

if __name__ == '__main__':
   app.run()