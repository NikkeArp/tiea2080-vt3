#!venv/bin/python
#-*- coding: utf-8 -*-

## My python modules
from mylogging import log_exception
from my_wtforms.admin import LoginForm
from my_wtforms.user import TeamForm, ModTeamForm
from flask_tools import save_json, load_json, admin_auth, json_loaded, url_exists

## Basic python modules
from functools import wraps
from uuid import uuid4

## Flask modules
from flask import Blueprint, flash, redirect, render_template, url_for
from flask.globals import current_app, g, request, session

admin = Blueprint('admin', __name__, url_prefix='/admin')
logging = current_app.logger


@admin.before_request
def before_request():
    g.data = load_json(current_app.config['JSONPATH'])
        

##              View-functions                  ##

@admin.route('/', methods=['GET', 'POST'])
@admin.route('/login', methods=['GET', 'POST'])
def login():
    '''Admin login'''
    form = LoginForm()
    if form.validate_on_submit():
        session['admin'] = {
            'logged': True 
        }
        return redirect(url_for('admin.home'))

    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@admin_auth
def logout():
    session.pop('admin')
    return redirect(url_for('admin.login'))

@admin.route('/home')
@admin_auth
@json_loaded
def home():
    return render_template('admin/home.html', races=map(lambda x: x['nimi'], g.data))

@admin.route('/<race_name>')
@json_loaded
@admin_auth
def race(race_name):
    '''Admin page for selected race'''
    for r in g.data:
        if r['nimi'] == race_name:
            race_data = {
                'name': r['nimi'],
                'series': map(lambda x: x['nimi'], r['sarjat'])
                }
            break
        else:
            race_data = None
    return render_template('admin/race.html', race_data=race_data)


@admin.route('/<race_name>/<series_name>', methods=['GET', 'POST'])
@json_loaded
@admin_auth
def series(race_name, series_name):

    g.race = race_name
    form = TeamForm()
    
    for race in g.data:
        if race['nimi'] == race_name:
            for series in race['sarjat']:
                if series['nimi'] == series_name:
                    series_data = series['joukkueet']
                    
                    if form.validate_on_submit():

                        new_team = {
                            'nimi': form.name.data,
                            'jasenet': filter(lambda x: x != '', [
                                    form.mem1.data, form.mem2.data, form.mem3.data,
                                    form.mem4.data, form.mem5.data,
                                ]),
                            'leimaustapa': ['GPS'],
                            'rastit' : [],
                            'id' : uuid4()
                        }
                        series['joukkueet'].append(new_team)
                        save_json(current_app.config['JSONPATH'], g.data)
                        
                        return redirect(url_for('admin.series',
                            race_name=race_name, series_name=series_name))
                    break
                else:
                    series_data = None

    return render_template('admin/series.html',
        series_data=series_data, form=form,
        race_name=race_name, series_name=series_name)

@admin.route('/<race_name>/<series_name>/<team_name>', methods=['GET', 'POST'])
@url_exists
@json_loaded
@admin_auth
def team(race_name, series_name, team_name):

    team = None
    for race in g.data:
        if race['nimi'] == race_name:
            for series in race['sarjat']:
                if series['nimi'] == series_name:
                    for t in series['joukkueet']:
                        if t['nimi'] == team_name:
                            team = g.team =  t
                            team['sarja'] = series_name
                            break
                if team: break
        if team: break

    form = ModTeamForm()
    form.init_series(race_name)

    if form.validate_on_submit():
        team = None
        ## Find team object from json-data.
        for race in g.data:
            if race['nimi'] == race_name:
                for series in race['sarjat']:
                    if series['nimi'] == series_name:
                        for i, t in enumerate(series['joukkueet']):
                            if t['nimi'] == team_name:
                                team = t
                                if form.series.data:
                                ## Delete team from old series
                                    del series['joukkueet'][i]
                                ## Modify team in place
                                else:
                                    t['nimi'] = form.name.data
                                    t['jasenet'] = filter(lambda x: x != u'', [
                                        form.mem1.data, form.mem2.data, form.mem3.data,
                                        form.mem4.data, form.mem5.data])
        ## Make changes to team and store it in new series.
        ## Update session var for series.                  
        if form.series.data:
            team['nimi'] = form.name.data
            team['jasenet'] = filter(lambda x: x != u'', [
                form.mem1.data, form.mem2.data, form.mem3.data,
                form.mem4.data, form.mem5.data])

            for race in g.data:
                if race['nimi'] == race_name:
                    for series in race['sarjat']:
                        if series['nimi'] == form.series.data:
                            series['joukkueet'].append(team)
        ## Save changes
        try:
            save_json(current_app.config['JSONPATH'], g.data)
        except:
            flash(u'Muutoksia ei voitu tallentaa!', 'error')
            return redirect(url_for('json_error'))

        ## Redirect user to same page.
        return redirect(url_for('admin.team',
           race_name=race_name,
           series_name=form.series.data,
           team_name=form.name.data))

    if not form.is_submitted():
        form.set_defaults(team)

    return render_template('admin/team.html',
        form=form)

