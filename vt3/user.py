#!venv/bin/python
#-*- coding: utf-8 -*-

## My python modules
from mylogging import log_exception
from flask_tools import (load_json, save_json,
    auth, json_loaded)
from my_wtforms.user import LoginForm, ModTeamForm

## Basic python modules
from functools import wraps

## Flask modules
from flask import Blueprint, flash, redirect, render_template, url_for
from flask.globals import current_app, g, request, session

user = Blueprint('user', __name__)
logging = current_app.logger

@user.before_request
def before_request():
    g.data = load_json(current_app.config['JSONPATH'])

##              View-functions                  ##

@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
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
@auth
def logout():
    '''Logout view-function. Clears session variables but
       sets logged_in to False. Redirects user to login-page.'''
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('user.login'))

@user.route('/teams')
@auth
@json_loaded
def teams():
    '''Teams view-function for selected race.
       Displays all teams and members.'''

    for r in g.data:
        race = r if r['nimi'] == session['race'] else None
        if race: break
    
    ## Sort series and teams
    race['sarjat'] = sorted(race['sarjat'], key=lambda x: x['nimi'])
    for series in race['sarjat']:
        series['joukkueet'].sort(key=lambda x: x['nimi'])
        for team in series['joukkueet']:
            team['jasenet'] = sorted(team['jasenet'])

    return render_template('user/teams.html',
        race=race)

@user.route('/team', methods=['GET', 'POST'])
@auth
@json_loaded
def team():
    '''Edit team view-function. Creates team editing form for user.'''

    form = ModTeamForm()
    g.race = session['race']
    form.init_series(session['race'])

    if form.validate_on_submit():
        team = None
        series_modified = True if session['user']['series'] != form.series.data else False    

        ## Find team object from json-data.
        for race in g.data:
            if race['nimi'] == session['race']:
                for series in race['sarjat']:
                    if series['nimi'] == session['user']['series']:
                        for i, t in enumerate(series['joukkueet']):
                            if t['id'] == session['user']['id']:
                                team = t
                                ## Delete team from old series
                                if series_modified:
                                    del series['joukkueet'][i]
                                ## Modify team in place
                                else:
                                    t['nimi'] = form.name.data
                                    t['jasenet'] = filter(lambda x: x != u'', [
                                        form.mem1.data, form.mem2.data, form.mem3.data,
                                        form.mem4.data, form.mem5.data])
        
        session['user']['name'] = form.name.data
        session['user']['members'] = filter(lambda x: x != u'', [
            form.mem1.data, form.mem2.data, form.mem3.data,
            form.mem4.data, form.mem5.data])
        
        ## Make changes to team and store it in new series.
        ## Update session var for series.                  
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

        ## Notify that mutable structure session-variables have changed.
        session.modified = True

        ## Save changes
        try:
            save_json(current_app.config['JSONPATH'], g.data)
        except:
            logging.debug(u'JSON didnt save')
            flash(u'Muutoksia ei voitu tallentaa!', 'error')
            return redirect(url_for('json_error'))
        
        ## Redirect user to same page.
        return redirect(url_for('user.team'))

    ## Set defaults in form fields
    if not form.is_submitted():
        form.set_defaults({
            'nimi': session['user']['name'],
            'sarja': session['user']['series'],
            'jasenet': session['user']['members']
        })

    return render_template('user/team.html', form=form)
