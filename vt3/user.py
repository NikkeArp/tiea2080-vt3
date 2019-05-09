#!venv/bin/python
#-*- coding: utf-8 -*-

## My python modules
from mylogging import log_exception
from my_wtforms.user import LoginForm

## Basic python modules
from functools import wraps

## Flask modules
from flask import Blueprint, flash, redirect, render_template, url_for
from flask.globals import current_app, g, request, session
import flask.json as json


##            Define user blueprint             ##

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
        log_in_view('JSON-data successfuly loaded')
    except:
        g.data = None
        log_in_view(log_exception(log))
        log_in_view('JSON-data didnt load!')


##    Decorator-functions for view-functions    ##

def log_debug(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        for x in log_messages:
            x[1].debug(x[0])
        return func(*args, **kwargs)
    return decorated
def authorized(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('user.login'))
        return func(*args, **kwargs)
    return decorated
def json_loaded(func):
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
    return render_template('JSON_e.html')

@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
@log_debug
@json_loaded
def login():
    '''Login view-function'''

    form = LoginForm()
    form.set_choices()

    if form.validate_on_submit():
        session['user'] = form.username.data
        log.debug(u'User {0} logged in'.format(session['user']))
        return u'Hello {0}!'.format(session['user'])

    return render_template('user/login.html',
        form=form)

