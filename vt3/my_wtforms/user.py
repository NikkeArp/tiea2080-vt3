#!venv/bin/python
# -*- coding: utf-8 -*-

## python modules
from hashlib import sha512

## My modules
from vt3.mylogging import log_exception

## Flask modules
from flask import g, current_app, session
from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SelectField, PasswordField,
    HiddenField, RadioField)
from wtforms import validators

logger = current_app.logger

def validate_teamname(form):
    '''Helper function to make sure user
    input teamname is unique'''

    ## No changes to teamname
    if session['user']['name'].upper() == form.name.data.upper():
        return True

    ## Find possible match from other teams
    for race in g.data:
        if race['nimi'] == session['race']:
            for series in race['sarjat']:
                for team in series['joukkueet']:
                    if team['nimi'].upper() == form.name.data.upper():
                        form.name.errors.append(u'Kilpailussa on jo joukkue tällä nimellä.')
                        return False
    ## Name is unique
    return True

def validate_team(data, form):
    for race in data:
        if race['nimi'] == form.race.data:
            for serie in race['sarjat']:
                for team in serie['joukkueet']:
                    
                    ## Ignore whitespace and capitalization
                    if team['nimi'].upper().strip() == form.username.data.upper():
                        g.team_name = team['nimi']
                        g.team = team
                        g.series = serie['nimi']
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
    '''Validates users input password by hashing it and 
    comparing to predefined password hash.'''
    
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
        validators=[validators.DataRequired()],
        #? Strip whitespace and raise to upper for validation
        filters=[lambda x: x.strip() if x else x])
    password = PasswordField(u'Salasana',
        validators=[validators.DataRequired()])
    race = SelectField(u'Kilpailu',
        validators=[validators.DataRequired()])
    
    def set_choices(self):
        '''Enables dynamic choices after forms creation'''
        races = []
        for i, race in enumerate(g.data):
            races.append((race['nimi'], race['nimi']))
        self.race.choices=races

    def validate(self):
        '''Basic validation with custom validators for
        username and password'''
        if FlaskForm.validate(self):
            if validate_team(g.data, self):
                if validate_password(self, self.password):
                    return True

        logger.debug('{0}s errors: {1}'.format(self, self.errors))
        return False
        
        
##                                                                ##
##                          EditUserForm                          ##
##                                                                ##


class EditTeamForm(FlaskForm):
    name = StringField(u'Nimi',
        validators=[validators.InputRequired()])

    series = RadioField(u'Sarja',
        validators=[validators.InputRequired()])

    mem1 = StringField(u'Jäsen 1')
    mem2 = StringField(u'Jäsen 2')
    mem3 = StringField(u'Jäsen 3')
    mem4 = StringField(u'Jäsen 4')
    mem5 = StringField(u'Jäsen 5')

    def validate(self):
        '''Basic validation with custom validators for team-members and
        teamname. Ensures team name is unique and team has min 2 members.'''
        if FlaskForm.validate(self):

            validation_results = []

            ##Validate team members, min 2
            members = [
                self.mem1.data,self.mem2.data,
                self.mem3.data,self.mem4.data,
                self.mem5.data
            ]
            if len(filter(lambda x: x != u'' and x != None, members)) >= 2:
                validation_results.append(True)
            else:
                self.mem1.errors.append(u'Vähintään 2 jäsentä')
                validation_results.append(False)

            ##Validate team name, unique name
            validation_results.append(validate_teamname(self))

            return all(validation_results)
        else:
            return False


    def init_series(self, race_name):
        '''Sets values to radiofield selections'''
        series = None
        for race in g.data:
            if race['nimi'] == race_name:
                series = race['sarjat']
        if series:
            series = map(lambda x: (x['nimi'], x['nimi']), series)
            self.series.choices = sorted(series)
            

    def set_defaults(self):
        '''Sets defailt values to form-fields'''
        self.name.default = session['user']['name']
        self.series.default = session['user']['series']
        
        try:
            self.mem1.default = session['user']['members'][0]
            self.mem2.default = session['user']['members'][1]
            self.mem3.default = session['user']['members'][2]
            self.mem4.default = session['user']['members'][3]
            self.mem5.default = session['user']['members'][4]
        except:
            pass

        self.process()

