#-*- coding: utf-8 -*-
from io import open
from mylogging import log_exception
from functools import wraps
from flask import flash, g, redirect, url_for, abort
from flask.globals import request, session, current_app
import flask.json as json

def save_json(json_path, data):
    '''Saves json-data to file'''
    with open(json_path, 'w', encoding='utf-8') as file:
        file.write(unicode(json.dumps(data,
            ensure_ascii=False,
            indent=2, separators=(',', ': '))))

##    Decorator-functions for view-functions    ##
def auth(func):
    '''Decorator function to make sure user is logged in
       before accessing content-pages. If not authorized,
       redirects user to login-page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        if session.get('user_logged'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user.login'))
    return decorated

def admin_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if session.get('admin_logged'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.login'))
    return decorated
    
def json_loaded(func):
    '''Decorator-function to ensure that JSON-data is
       loaded before executing view-function.
       Redirects user to JSON-error page.'''
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            with open(current_app.config['JSONPATH'], encoding='utf-8') as file:
                g.data = json.load(file)
        except:
            g.data =  None
        if not g.data:
            flash('JSON-tiedostoa ei voitu ladata', 'error')
            log_exception(current_app.logger)
            return redirect(url_for('json_error'))
        return func(*args, **kwargs)
    return decorated

class back(object):
    cfg = current_app.config.get
    cookie = cfg('REDIRECT_BACK_COOKIE', 'back')
    default_view = cfg('REDIRECT_BACK_DEFAULT', 'admin.home')

    @staticmethod
    def anchor(func, cookie=cookie):
        @wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.url
            return func(*args, **kwargs)
        return result

    @staticmethod
    def url(default=default_view, cookie=cookie):
        return session.get(cookie, url_for(default))

    @staticmethod
    def redirect(default=default_view, cookie=cookie):
        return redirect(back.url(default, cookie))
back = back()