#!/usr/bin/env python3
import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base
from flask_assets import Environment, Bundle
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

import app.logging

import logging

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
assets = Environment()
csrf = CSRFProtect()
Base = declarative_base()


logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    logger.info("Creating app")
    assets._named_bundles = {}
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as e:
        logger.info(f"Exception occured: {e} ")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    assets.init_app(app)

    from . import auth
    logger.debug("Registering blueprint auth")
    app.register_blueprint(auth.bp)

    from . import main
    logger.debug("Registering blueprint main")
    app.register_blueprint(main.bp)

    from . import profile
    logger.debug("Registering blueprint profile")
    app.register_blueprint(profile.bp, url_prefix='/profile')

    from . import charactersheet
    logger.debug("Registering blueprint charactersheet")
    app.register_blueprint(charactersheet.bp, url_prefix='/character')
    app.register_blueprint(charactersheet.api, url_prefix='/api/character')

    app.add_url_rule('/', endpoint='profile.index')

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    with app.app_context():

        logger.debug("Registering assets")
        assets.url = app.static_url_path
        assets.config['TYPESCRIPT_CONFIG'] = '--target ES6'
        scss = Bundle('scss/main.scss', 'scss/character.scss',
                      filters='pyscss',
                      output='css/all.css')
        assets.register('scss_all', scss)

        ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
        assets.register('ts_coc', ts_coc)

    return app
