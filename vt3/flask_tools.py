#!venv/bin/python
#-*- coding: utf-8 -*-

from functools import wraps

from flask import flash, g, redirect, url_for
from mylogging import log_exception
from flask.globals import request, session, current_app
import flask.json as json

##        Load race-data from data.json         ##

def load_json(json_path):
    '''Loads json-file and returns it converted to
    python'''
    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except:
        return None

def save_json(json_path, data):
    '''Saves json-data to file'''
    with open(json_path, 'w') as file:
        json.dump(data, file)

##    Decorator-functions for view-functions    ##
 

def url_exists(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        #TODO    JA TÄÄ PASKA TOIISNDIANDSDBIABFIBUFCBABFOSD

def auth(func):
    '''Decorator function to make sure user is logged in
       before accessing content-pages. If not authorized,
       redirects user to login-page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('user.login'))
        return func(*args, **kwargs)
    return decorated

def admin_auth(func):
    '''Decorator function to make sure admin is logged in
       before accessing admin-pages. If not authorized,
       redirects admin to login-page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        if not session.get('admin')['logged']:
            return redirect(url_for('admin.login'))
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
            return redirect(url_for('json_error'))
        return func(*args, **kwargs)
    return decorated