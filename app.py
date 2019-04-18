#!venv/bin/python
# -*- coding: utf-8 -*-

import hashlib
import logging
from flask import Flask, render_template, url_for

#---------DEBUG SETTINGS----------#
logging.basicConfig(filename='logs/server.log', level=logging.DEBUG)
#---------------------------------#

#--------App configurations-------#
app = Flask(__name__)
app.secret_key='dbd238d94e15178b1e6440b09749d1e66847152487e932df0ffc0536b78ff2a5d9f50a6aa15418d78cd1cade996fada634635aba4cba673b6754ecf89c26a096'
#---------------------------------#


@app.route('/')
def index():
    logging.info("Rendered index template")
    return render_template("index.html")



if __name__ == '__main__':
    app.run(debug=True)