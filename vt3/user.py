#!venv/bin/python
#-*- coding: utf-8 -*-

## My python modules
from mylogging import log_exception
from my_wtforms.user import LoginForm, EditTeamForm

## Basic python modules
from functools import wraps

## Flask modules
from flask import Blueprint, flash, redirect, render_template, url_for
from flask.globals import current_app, g, request, session
import flask.json as json

user = Blueprint('user', __name__)
log = current_app.logger

log_messages = []
def log_in_view(message, logger=log):
    log_messages.append((message, logger))

##        Load race-data from data.json         ##

@user.before_request
def before_request():
    try:
        with open(current_app.config['JSONPATH'], 'r') as file:
            g.data = json.load(file)
    except:
        g.data = None
        log_in_view(log_exception(log))
        log_in_view('JSON-data didnt load!')
        

def save_json():
    try:
        with open(current_app.config['JSONPATH'], 'w') as file:
            json.dump(g.data, file)
    except:
        log_in_view(log_exception(log))
        log_in_view('JSON didnt get saved!')

##    Decorator-functions for view-functions    ##

def log_debug(func):
    '''Decorator function to log messages in view-function.
       This way, debug-toolbar can show logged messages outside
       of view-functions.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        for x in log_messages:
            x[1].debug(x[0])
        return func(*args, **kwargs)
    return decorated
def authorized(func):
    '''Decorator function to make sure user is logged in
       before accessing content-pages. If not authorized,
       redirects user to login-page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('user.login'))
        return func(*args, **kwargs)
    return decorated
def json_loaded(func):
    '''Decorator-function to ensure that JSON-data is
       loaded before executing view-function.
       Redirects user to JSON-error page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        if not getattr(g, 'data', None):
            flash('JSON-tiedostoa ei voitu ladata', 'error')
            return redirect(url_for('user.json_error'))
        return func(*args, **kwargs)
    return decorated

##              View-functions                  ##

@user.route('/json-error')
def json_error():
    '''JSON-error page to inform user about JSON-error.'''
    return render_template('JSON_e.html')

@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
##@log_debug
@json_loaded
def login():
    '''Login view-function'''

    ## Initialize login-form and set choices dynamically.
    form = LoginForm()
    form.set_choices()

    if form.validate_on_submit():
        session['user'] = {
            'name': g.team['nimi'], #? Actual teamname from validation (not user input).
            'series': g.series, #? Series from validation
            'members': sorted(g.team['jasenet']), #? Team members from validation
            'id': g.team['id']
        } 
        session['race'] = form.race.data  #? Race name from form.
        session['logged_in'] = True

        ## Redirect user to their races teams-page
        return redirect(url_for('user.teams'))

    ## Render login-page
    return render_template('user/login.html',
        form=form)

@user.route('/logout')
@authorized
##@log_debug
def logout():
    '''Logout view-function. Clears session variables but
       sets logged_in to False. Redirects user to login-page.'''
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('user.login'))


@user.route('/teams')
@authorized
@log_debug
@json_loaded
##@log_debug
def teams():
    '''Teams view-function for selected race.
       Displays all teams and members.'''

    for r in g.data:
        race = r if r['nimi'] == session['race'] else None
        if race: break
    
    race['sarjat'] = sorted(race['sarjat'], key=lambda x: x['nimi'])
    return render_template('user/teams.html',
        race=race)


@user.route('/team', methods=['GET', 'POST'])
@authorized
@json_loaded
def team():

    form = EditTeamForm()
    form.init_series(session['race'])

    if form.validate_on_submit():

        team = None
        series_modified = True if session['user']['series'] != form.series.data else False    

        for race in g.data:
            if race['nimi'] == session['race']:
                for series in race['sarjat']:
                    if series['nimi'] == session['user']['series']:
                        for i, t in enumerate(series['joukkueet']):
                            if t['id'] == session['user']['id']:
                                team = t
                                if series_modified:
                                    del series['joukkueet'][i]
                                else:
                                    t['nimi'] = form.name.data
                                    t['jasenet'] = filter(lambda x: x != u'', [
                                        form.mem1.data, form.mem2.data, form.mem3.data,
                                        form.mem4.data, form.mem5.data])
        
        session['user']['name'] = form.name.data
        session['user']['members'] = filter(lambda x: x != u'', [
            form.mem1.data, form.mem2.data, form.mem3.data,
            form.mem4.data, form.mem5.data])
        
        if series_modified:
            session['user']['series'] = form.series.data
            
            team['nimi'] = form.name.data
            team['jasenet'] = filter(lambda x: x != u'', [
                form.mem1.data, form.mem2.data, form.mem3.data,
                form.mem4.data, form.mem5.data])

            for race in g.data:
                if race['nimi'] == session['race']:
                    for series in race['sarjat']:
                        if series['nimi'] == session['user']['series']:
                            series['joukkueet'].append(team)
                            log.debug(team)

        session.modified = True
        save_json()
        return redirect(url_for('user.team'))

    if not form.is_submitted():
        form.set_defaults()

    return render_template('user/team.html', form=form)
