#!venv/bin/python
#-*- coding: utf-8 -*-

from flask import g, session, current_app
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SelectField, RadioField
from wtforms import validators

from hashlib import sha512

class LoginForm(FlaskForm):
    '''Login form with name pass and race fields'''
    name = StringField(u'Joukkue',
        validators=[validators.InputRequired()],
        filters=[lambda x: x.strip() if x else x])

    password = PasswordField(u'Salasana',
        validators=[validators.InputRequired()])

    race = SelectField(u'Kilpailu', coerce=unicode,
        validators=[validators.InputRequired()])

    def init_form(self, races):
        '''Sets choices to race selection dynamically'''
        self.race.choices = map(lambda x: (x['nimi'], x['nimi']), races)

    def validate(self):
        '''Custom validation built over default FlaskForm
        validation. Validates username, password and race.
        Error feedback to user accordingly.
        '''
        found = False

        ## Default validation
        if FlaskForm.validate(self):
            val_results = [] ## Validation results will be stored here
            
            ## VALIDATE USERNAME
            for race in g.data:
                if race['nimi'] == self.race.data:
                    series = race.get('sarjat')

                    if series is None: ## Make sure data contains series and teams
                        self.name.errors.append(u'Kilpailussa ei ole sarjoja')
                        return False ## Whole validation has failed failed
                    for serie in series:
                        for team in serie['joukkueet']:
                            if team['nimi'].upper().strip() == self.name.data.upper():
                                ## Team found from data

                                ## Remove useless heavy stuff.
                                race.pop('rastit', None)
                                race.pop('tupa', None) 
                                g.race = race

                                team['sarja'] = serie['nimi']
                                g.team = team
                                found = True
                                break
                if found: break
            
            ## Search elsewhere.
            if not found:
                def any_race():
                    for race in g.data:
                        if not race.get('sarjat'):
                            continue ## Race doesnt contain series or teams
                        for serie in race['sarjat']:
                            for team in serie['joukkueet']:
                                if team['nimi'] == self.name.data:
                                    ## Team found in data, race must be wrong.
                                    self.race.errors.append(u'Väärä kilpailu')
                                    return True
                    return False

                if not any_race():
                    ## No such team exists.
                    self.name.errors.append(u'Väärä joukkue')
                val_results.append(False)

            ## VALIDATE PASSWORD
            hasher = sha512(current_app.config['SECRET_KEY'] +
                str(self.password.data))
            if hasher.hexdigest() != current_app.config['PASS_W']:
                field.errors.append(u'Väärä salasana')
                val_results.append(False)
            
            ## Check if results contain failed validations
            return all(val_results)


class TeamForm(FlaskForm):
    name = StringField(u'Nimi',
        validators=[validators.InputRequired()])

    mem1 = StringField(u'Jäsen 1')
    mem2 = StringField(u'Jäsen 2')
    mem3 = StringField(u'Jäsen 3')
    mem4 = StringField(u'Jäsen 4')
    mem5 = StringField(u'Jäsen 5')

    def validate(self):
        '''
        Custom validation with validators for team-members and
        teamname. Ensures team name is unique and team has min
        2 members.
        '''
        if FlaskForm.validate(self):

            members = [
                self.mem1.data, self.mem2.data, self.mem3.data,
                self.mem4.data, self.mem5.data
            ]
            val_results = [] ## Valdiation results will be stored here

            if self.name.data.upper() != session['user']['nimi'].upper():
                ## seach for dublicate teamname
                for race in g.data:
                    if race['nimi'] == session['race']['nimi']:
                        for series in race['sarjat']:
                            for team in series['joukkueet']:
                                if team['nimi'].upper() == self.name.data.upper():
                                    self.name.errors.append(
                                        u'Kilpailussa on jo joukkue tällä nimellä.')
                                    val_results.append(False)    

            ## Ensure that team has atleast 2 members
            if len(filter(lambda x: x != u'' and x != None, members)) < 2:
                self.mem1.errors.append(u'Vähintään 2 jäsentä')
                val_results.append(False)

            ## Check if results contain failed validations
            return all(val_results)
        else:
            return False


class UserTeamForm(TeamForm):
    '''Form for users to modify their teams'''
    series = RadioField(u'Sarja')

    def init_form(self, data):
        '''Sets race series dynamically'''
        for race in data:
            if race['nimi'] == session['race']['nimi']:
                series = race['sarjat']
                break
            else:
                series = None
        if series:
            self.series.choices=map(lambda x: (x['nimi'], x['nimi']),
                sorted(series, key=lambda y: y['nimi']))
    
    def set_defaults(self, team):
        '''Sets default values for form fields'''
        self.name.default = team['nimi']
        self.series.default = team['sarja']
        try:
            self.mem1.default = team['jasenet'][0]
            self.mem2.default = team['jasenet'][1]
            self.mem3.default = team['jasenet'][2]
            self.mem4.default = team['jasenet'][3]
            self.mem5.default = team['jasenet'][4]
        except:
            pass
        self.process()

class PasswordForm(FlaskForm):
    password = PasswordField(u'Salasana',
        validators=[validators.InputRequired()])
    
    def validate(self):
        if FlaskForm.validate(self):
            ## VALIDATE PASSWORD
            hasher = sha512(current_app.config['SECRET_KEY'] +
                str(self.password.data))
            if hasher.hexdigest() != current_app.config['ADMIN_PASS_W']:
                field.errors.append(u'Väärä salasana')
                return False
            return True


class AddTeamForm(TeamForm):

    def validate(self):
        if FlaskForm.validate(self):

            members = [
                self.mem1.data, self.mem2.data, self.mem3.data,
                self.mem4.data, self.mem5.data
            ]
            val_results = [] ## Valdiation results will be stored here

            ## seach for dublicate teamname
            for race in g.data:
                if race['nimi'] == g.race['nimi']:
                    for series in race['sarjat']:
                        for team in series['joukkueet']:
                            if team['nimi'].upper() == self.name.data.upper():
                                self.name.errors.append(u'Kilpailussa on jo joukkue tällä nimellä.')
                                val_results.append(False)    

            ## Ensure that team has atleast 2 members
            if len(filter(lambda x: x != u'' and x != None, members)) < 2:
                self.mem1.errors.append(u'Vähintään 2 jäsentä')
                val_results.append(False)

            ## Check if results contain failed validations
            return all(val_results)
        else:
            return False

class AdminTeamForm(TeamForm):
    delete = BooleanField(u'Poista')
    series = RadioField(u'Sarja')
    
    def set_defaults(self, team):
        '''Sets default values for form fields'''
        self.name.default = team['nimi']
        self.series.default = g.serie
        try:
            self.mem1.default = team['jasenet'][0]
            self.mem2.default = team['jasenet'][1]
            self.mem3.default = team['jasenet'][2]
            self.mem4.default = team['jasenet'][3]
            self.mem5.default = team['jasenet'][4]
        except:
            pass
        self.process()

    def init_form(self):
        '''Sets race series dynamically'''
        for race in g.data:
            if race['nimi'] == g.race:
                series = race['sarjat']
                break
            else:
                series = None
        if series:
            self.series.choices=map(lambda x: (x['nimi'], x['nimi']),
                sorted(series, key=lambda y: y['nimi']))

    def validate(self):
        if self.delete.data:
            return True

        if FlaskForm.validate(self):
            members = [
                self.mem1.data, self.mem2.data, self.mem3.data,
                self.mem4.data, self.mem5.data
            ]
            val_results = [] ## Valdiation results will be stored here
            
            ## If same username than before, no need to check others
            if self.name.data != g.team['nimi']:
                ## seach for dublicate teamname
                for race in g.data:
                    if race['nimi'] == g.race:
                        for series in race['sarjat']:
                            for team in series['joukkueet']:
                                if team['nimi'].upper() == self.name.data.upper():
                                    self.name.errors.append(u'Kilpailussa on jo joukkue tällä nimellä.')
                                    val_results.append(False)    

            ## Ensure that team has atleast 2 members
            if len(filter(lambda x: x != u'' and x != None, members)) < 2:
                self.mem1.errors.append(u'Vähintään 2 jäsentä')
                val_results.append(False)

            ## Check if results contain failed validations
            return all(val_results)
        else:
            return False


