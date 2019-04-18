#!venv/bin/python
# -*- coding: utf-8 -*-

#Basic modules
import simplejson as json
import hashlib
import os

#My modules
from mylogging import log_exc, logging

#Flask modules
from flask_wtf import FlaskForm
from wtforms import StringField, Form, validators, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, url_for, redirect, request, session


#--------App configurations-------#
app = Flask(__name__)
app.secret_key='dbd238d94e15178b1e6440b09749d1e66847152487e932df0ffc0536b78ff2a5d9f50a6aa15418d78cd1cade996fada634635aba4cba673b6754ecf89c26a096'
#---------------------------------#


#----------Load json--------------#
try:
    with open("data/data.json") as file:
        data = json.load(file)
except:
    log_exc()
    logging.warning("DATA-JSON DIDN'T LOAD!")
    data = None
#---------------------------------#

###################################
##          WTF-FORMS            ##
###################################


###################################
##            ROUTES             ##
###################################

@app.route('/', methods=("GET", "POST"))
def index():
    return render_template("index.html")
    

###################################
##           RUN APP             ##
###################################

if __name__ == '__main__':
    logging.info("App is running! http://127.0.0.1:5000/\n")
    app.run(debug=True)