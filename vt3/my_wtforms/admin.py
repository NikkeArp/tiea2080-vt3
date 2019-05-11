#!venv/bin/python
# -*- coding: utf-8 -*-

## python modules
from hashlib import sha512

## My modules
from vt3.mylogging import log_exception
from .user import TeamForm

## Flask modules
from flask import g, current_app, session
from flask_wtf import FlaskForm
from wtforms.fields import (StringField, PasswordField,
    HiddenField, RadioField)
from wtforms import validators

logger = current_app.logger


##                                           ##
##             ADMIN LOGIN FORM              ##
##                                           ##

class LoginForm(FlaskForm):
    password = PasswordField(u'Salasana',
        validators=[validators.InputRequired()])
    
    def validate(self):
        if FlaskForm.validate(self):
            hasher = sha512()
            hasher.update(current_app.config['SECRET_KEY'])
            hasher.update(self.password.data)

            if hasher.hexdigest() == current_app.config['ADMIN_PASS_W']:
                return True
            else:
                self.password.errors.append(u'Väärä salasana')
                return False
        return False
