#!/usr/bin/env python3
import os

from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy

from functools import reduce
from sqlalchemy.ext.declarative import declarative_base
from flask_assets import Environment, Bundle
from flask_login import LoginManager
from flask_migrate import Migrate, upgrade
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
assets = Environment()

Base = declarative_base()

def create_app(test_config=None):
    global assets
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

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


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    mail.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    from . import charactersheet
    app.register_blueprint(charactersheet.bp, url_prefix='/character')
    app.register_blueprint(charactersheet.api, url_prefix='/api/character')
    
    app.add_url_rule('/', endpoint='index')
    
    return app
