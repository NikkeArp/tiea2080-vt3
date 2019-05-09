#!venv/bin/python
# -*- coding: utf-8 -*-

## python modules
from hashlib import sha512

## My modules
from vt3.mylogging import log_exception

## Flask modules
from flask import g, current_app
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField, PasswordField
from wtforms import validators

logger = current_app.logger

def validate_team(data, form):
    for race in data:
        if race['nimi'] == form.race.data:
            for serie in race['sarjat']:
                for team in serie['joukkueet']:
                    if team['nimi'] == form.username.data:
                        return True
    def any_race():
        for race in data:
            for serie in race['sarjat']:
                for team in serie['joukkueet']:
                    if team['nimi'] == form.username.data:
                        form.race.errors.append(u'Väärä kilpailu')
                        return True
        return False

    if not any_race():
        form.username.errors.append(u'Väärä joukkue')

    return False

def validate_password(form, field):
    hasher = sha512(current_app.config['SECRET_KEY'] +
        str(field.data))
    if hasher.hexdigest() == current_app.config['PASS_W']:
        return True
    field.errors.append(u'Väärä salasana')
    return False



class LoginForm(FlaskForm):
    '''Login form with username,
    password and race select. Race choises
    are set dynamically after form initialization.'''

    username = StringField(u'Joukkue',
        validators=[validators.DataRequired()])
    password = PasswordField(u'Salasana',
        validators=[validators.DataRequired()])
    race = SelectField(u'Kilpailu',
        validators=[validators.DataRequired()])
    
    def set_choices(self):
        races = []
        for i, race in enumerate(g.data):
            races.append((race['nimi'], race['nimi']))
        self.race.choices=races

    def validate(self):
        if FlaskForm.validate(self):

            if validate_team(g.data, self):
                if validate_password(self, self.password):
                    return True

        logger.debug('{0}s errors: {1}'.format(self, self.errors))
        return False
        
        

