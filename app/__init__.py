#!/usr/bin/env python3
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_assets import Environment, Bundle
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
assets = None

Base = declarative_base()

def create_app(test_config=None):
    global assets
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'whathappened.sqlite'),
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.instance_path, 'whathappened.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    assets = Environment(app)
    assets.url = app.static_url_path
    assets.config['TYPESCRIPT_CONFIG'] = '--target ES6'
    scss = Bundle('main.scss', 'character.scss', filters='pyscss', output='all.css')
    assets.register('scss_all', scss)


    @app.route('/hello')
    def hello():
        return "Hello, World!"
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from . import auth
    app.register_blueprint(auth.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    from . import charactersheet
    app.register_blueprint(charactersheet.bp, url_prefix='/character')
    app.register_blueprint(charactersheet.api, url_prefix='/api/character')
    
    app.add_url_rule('/', endpoint='index')
    
    return app
