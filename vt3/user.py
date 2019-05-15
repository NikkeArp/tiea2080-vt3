#!venv/bin/python
#-*- coding: utf-8 -*-

from functools import wraps
from mylogging import log_exception
from flasktools import json_loaded, auth, save_json

from flask import g, session, redirect, url_for, current_app, Blueprint, flash, render_template
from forms import LoginForm, UserTeamForm

user = Blueprint('user', __name__)
logging = current_app.logger


@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
@json_loaded
def login():
    '''View with simple login-form.'''
    form = LoginForm()
    form.init_form(g.data)
    if form.validate_on_submit():
        session['user_logged'] = True
        session['race'] = g.race
        session['user'] = g.team
        return redirect(url_for('user.teams'))
    return render_template('user/login.html', form=form)

@user.route('/logout')
@auth
def logout():
    session.clear()
    return redirect(url_for('user.login'))


@user.route('/teams')
@auth
@json_loaded
def teams():
    '''Teams view-function for selected race.
    Displays all teams and members.
    '''

    ## Find race from data
    for r in g.data:
        race = r if r['nimi'] == session['race']['nimi'] else None
        if race: break
    
    ## Sort series and teams
    if race.get('sarjat'):
        race['sarjat'].sort(key=lambda x: x['nimi'])

        for series in race['sarjat']:
            series['joukkueet'].sort(key=lambda x: x['nimi'])
            for team in series['joukkueet']:
                team['jasenet'].sort()
    
    ## Render race-page
    return render_template('user/teams.html',
        race=race)
    

@user.route('/team', methods=['GET', 'POST'])
@auth
@json_loaded
def team():
    '''View function for users team modification page.
    Renders form where user can make changes for teamname, series
    and team members. If inputs are valid saves changes to data.json
    and returns user back to team-listing page. Otherwise informs user
    what caused validation errors.'''
    form = UserTeamForm()
    form.init_form(g.data)
    if form.validate_on_submit():

        ## Series has changed.
        ## This flag will guide the flow in this function.
        s_changed = form.series.data != session['user']['sarja']
        team = None

        ## Gather and filter team members from form.
        session['user']['jasenet'] = filter(lambda x: x != u'' and x != None,
            [ 
                form.mem1.data, form.mem2.data,
                form.mem3.data, form.mem4.data, form.mem5.data,
            ])
        session.modified = True

        for race in g.data: ## Find race loacion inside json-data.
            if race['nimi'] == session['race']['nimi']:
                for serie in race['sarjat']:
                    if serie['nimi'] == session['user']['sarja']:
                        for i, t in enumerate(serie['joukkueet']):
                            if t['nimi'] == session['user']['nimi']:
                                ##    Team found     
                                if s_changed:
                                    ## Series changed 
                                    team = t
                                    team['nimi'] = session['user']['nimi'] = form.name.data
                                    team['jasenet'] = session['user']['jasenet']
                                    team['sarja'] = session['user']['sarja'] = form.series.data
                                    ## Delete old team 
                                    del serie['joukkueet'][i]
                                else:
                                    ## Update team in place 
                                    t['nimi'] = session['user']['nimi'] = form.name.data
                                    t['jasenet'] = session['user']['jasenet']
                                    ## Save changes to data.json-file 
                                    save_json(current_app.config['JSONPATH'], g.data)
                                    ## Redirect user to teams-page 
                                    return redirect(url_for('user.teams'))
        if team and s_changed:
            ## Move team to new series 
            for race in g.data:
                if race['nimi'] == session['race']['nimi']:
                    for series in race['sarjat']:
                        if series['nimi'] == session['user']['sarja']:
                            ## Append to teams and save changes to file. 
                            series['joukkueet'].append(team)
                            save_json(current_app.config['JSONPATH'], g.data)
                            ## Redired user to teams-page 
                            return redirect(url_for('user.teams'))
    
    ## Form is not submitted -> set default values 
    if not form.is_submitted():
        form.set_defaults(session['user'])

    ## Teams chekcpoints
    for race in g.data:
        if race['nimi'] == session['race']['nimi']:
            tupa = race['tupa']
            team_cps = []
            for x in tupa:
                if x['joukkue'] == session['user']['id']:
                    for race_cp in race['rastit']:
                        if race_cp['id'] == x['rasti']:
                            x['koodi'] = race_cp['koodi']
                            team_cps.append(x)
    return render_template('user/team.html',
        form=form, team_cps=team_cps)