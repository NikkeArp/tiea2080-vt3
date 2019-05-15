#!venv/bin/python
#-*- coding: utf-8 -*-

from uuid import uuid4
from functools import wraps
from mylogging import log_exception
from flasktools import json_loaded, admin_auth, save_json, back

from flask import g, session, redirect, url_for, current_app, Blueprint, flash, render_template, request, abort
from forms import PasswordForm, AddTeamForm, AdminTeamForm

admin = Blueprint('admin', __name__, url_prefix='/admin')
logging = current_app.logger

@admin.route('/', methods=['GET', 'POST'])
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = PasswordForm()

    if form.validate_on_submit():
        session.clear()
        session['admin_logged'] = True
        return redirect(url_for('admin.home'))

    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@admin_auth
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@admin.route('/koti')
@admin_auth
@json_loaded
def home():
    return render_template('admin/home.html',
         races=map(lambda x:{'nimi': x['nimi']}, g.data))

@admin.route('/kilpailu', methods=['GET', 'POST'])
@admin_auth
@json_loaded
def race():
    '''Race listing view'''
    race_arg = request.args.get('nimi')
    for race in g.data:
        if race['nimi'] == race_arg:
            return render_template('admin/race.html', race=race)
    return abort(404)

@admin.route('/sarja', methods=['GET', 'POST'])
@admin_auth
@json_loaded
@back.anchor ## Anchors url for return from editing team
def serie():
    '''Displays series data. Allows admin to create new
    team to series.'''
    serie_arg = request.args.get('nimi')
    race_arg = request.args.get('kilpailu')

    if serie_arg and race_arg:
        for race in g.data:
            if race['nimi'] == race_arg:
                for serie in race['sarjat']:
                    if serie['nimi'] == serie_arg:

                        ## Variables for validiation
                        g.race = race

                        form = AddTeamForm()
                        if form.validate_on_submit():
                            if serie.get('joukkueet'):
                                serie['joukkueet'].append({
                                    'nimi': form.name.data,
                                    'last': None,
                                    'jasenet': filter(lambda x: x != '' and x != None, [
                                        form.mem1.data, form.mem2.data, form.mem4.data,
                                        form.mem4.data, form.mem5.data,
                                        ]),
                                    'id': uuid4().int
                                })
                                ## Save changes to file
                                save_json(current_app.config['JSONPATH'], g.data)

                                logging.debug(request.url)
                                return back.redirect()
                        return render_template('admin/series.html',
                            form=form, serie=serie, race=race_arg)
        return back.redirect()
    return abort(404)

@admin.route('/joukkue', methods=['GET', 'POST'])
@admin_auth
@json_loaded
def team():
    '''Allows admin to modify teams data. Returns user back to
    series view.'''
    serie_arg = request.args.get('sarja')
    race_arg = request.args.get('kilpailu')
    team_arg = request.args.get('nimi')

    if serie_arg and race_arg and team_arg:
        for race in g.data:
            if race['nimi'] == race_arg:
                if not race['sarjat']:
                    return abort(404)
                for serie in race['sarjat']:
                    if serie['nimi'] == serie_arg:
                        for i, team in enumerate(serie['joukkueet']):
                            if team['nimi'] == team_arg:
                                ## Variables for validation
                                g.race = race['nimi']
                                g.serie = serie['nimi']
                                g.team = team

                                form = AdminTeamForm()
                                form.init_form()
                                if form.validate_on_submit():

                                    if form.delete.data:
                                        if not team_cps(race, team['id']):
                                            del serie['joukkueet'][i]
                                            save_json(current_app.config['JSONPATH'], g.data)
                                        else:
                                            flash(u'Joukkueella rastileimauksia. Poisto peruutettu!', 'error')
                                    elif form.series.data == serie['nimi']:
                                        ## edit team in place
                                        team = update_team(team, form)
                                        ## Save changes to file
                                        save_json(current_app.config['JSONPATH'], g.data)
                                    else:
                                        ## Delete old team after updating it
                                        new_team = update_team(team, form)
                                        del serie['joukkueet'][i]
                                        append_team(team, race, form.series.data)
                                        ## Save changes to file
                                        save_json(current_app.config['JSONPATH'], g.data)

                                    ## Return user to same page with updated data
                                    return back.redirect()
                                ## Form is not submitted, set default values
                                if not form.is_submitted():
                                    form.set_defaults(team)
                                ## Render page
                                return render_template('admin/team.html', form=form)
        return back.redirect()
    return abort(404)

@admin.route('/rastit')
@admin_auth
@json_loaded
def checkpoints():
    race_cps = []
    for i, race in enumerate(g.data):
        race_cps.append({
            'nimi': race['nimi'],
            'cps': []
        })
        if race.get('tupa'):
            for cp in race['tupa']:
                if not contains(race_cps[i]['cps'], cp):
                    for x in race['rastit']:
                        if x['id'] == cp['rasti']:
                            cp['count'] = 0
                            cp['data'] = x
                            race_cps[i]['cps'].append(cp)
    return render_template('admin/cps.html', race_cps=race_cps)


def contains(list_obj, item):
    for i, x in enumerate(list_obj):
        if x['rasti'] == item['rasti']:
            list_obj[i]['count'] += 1
            return True
    return False
        
def team_cps(race, team_id):
    for x in race['tupa']:
        if x['joukkue'] == team_id:
            return True
    return False
  


## HELPER FUNCTIONS ##
def update_team(team, form):
    '''Updates team data from form'''
    team['nimi'] = form.name.data
    team['jasenet'] = filter(lambda x: x != '' and x != None, [
        form.mem1.data, form.mem2.data, form.mem3.data,
        form.mem4.data, form.mem5.data,
        ])
    return team

def append_team(team, race, serie_name):
    '''Adds team to series'''
    for serie in race['sarjat']:
        if serie['nimi'] == serie_name:
            serie['joukkueet'].append(team)

def count_checkpoints(data, race_name):
    for race in data:
        if race['nimi'] == race_name:
                checkpoints = race['rastit']
                for series in race['sarjat']:
                    for team in series['joukkueet']:
                        for cp in team['rastit']:
                            for i, c in enumerate(checkpoints):
                                if c['id'] == cp['rasti']:
                                    if checkpoints[i].get('count'):
                                        checkpoints[i]['count'] += 1
                                    else:
                                        checkpoints[i]['count'] = 1
                return checkpoints
    return None