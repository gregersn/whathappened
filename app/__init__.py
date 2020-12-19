#!/usr/bin/env python3
import os

from flask import Flask
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base
from flask_assets import Environment, Bundle
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_webpackext import FlaskWebpackExt

import app.logging as applogging  # noqa imported for side effects

import logging

from config import Config

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

sql_alchemy_metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=sql_alchemy_metadata)
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
assets = Environment()
csrf = CSRFProtect()
webpackext = FlaskWebpackExt()
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

    # Init addons
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    webpackext.init_app(app)
    assets.init_app(app)

    # Register blueprints
    from . import auth
    logger.debug("Registering blueprint auth")
    app.register_blueprint(auth.bp)

    from . import main
    logger.debug("Registering blueprint main")
    app.register_blueprint(main.bp)

    from . import profile
    logger.debug("Registering blueprint profile")
    app.register_blueprint(profile.bp, url_prefix='/profile')

    from . import userassets
    logger.debug("Registering assets module")
    app.register_blueprint(userassets.bp, url_prefix='/assets')
    app.register_blueprint(userassets.apibp, url_prefix='/api/assets')

    from . import character
    logger.debug("Registering blueprint character")
    app.register_blueprint(character.bp, url_prefix='/character')
    app.register_blueprint(character.api, url_prefix='/api/character')
    character.register_assets(assets)

    from . import campaign
    app.register_blueprint(campaign.bp, url_prefix='/campaign')
    app.register_blueprint(campaign.apibp, url_prefix='/api/campaign')
    campaign.register_assets(assets)

    app.add_url_rule('/', endpoint='profile.index')

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    with app.app_context():

        logger.debug("Registering assets")
        assets.url = app.static_url_path
        assets.config['TYPESCRIPT_CONFIG'] = '--target ES6'

        scss = Bundle('scss/main.scss',
                      filters='pyscss',
                      output='css/all.css')
        assets.register('scss_all', scss)

        css_profile = Bundle('scss/profile.scss',
                             filters='pyscss',
                             output='css/profile.css')
        assets.register('scss_profile', css_profile)

        css_handout = Bundle('scss/handout.scss',
                             filters='pyscss',
                             output='css/handout.css')
        assets.register('scss_handout', css_handout)

    return app
