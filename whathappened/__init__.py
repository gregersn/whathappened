#!/usr/bin/env python3
import os

from flask import Flask
from flask_assets import Environment, Bundle
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_webpackext import FlaskWebpackExt

import logging

from typing import Type
from .database import init_db, session
from .config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # type: ignore  # Not an error

mail = Mail()
assets = Environment()
csrf = CSRFProtect()
webpackext = FlaskWebpackExt()

logger = logging.getLogger(__name__)


def create_app(test_config=None) -> Flask:
    logger.info("Creating app")
    assets._named_bundles = {}
    app = Flask(__name__, instance_relative_config=True)

    # Default settings
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(app.instance_path, 'whathappened.sqlite')

    )
    app.config.from_object(Config)

    # Load settings from environment
    loaded_config = False

    # Config file with settings used for development or in source tree mode
    loaded_config = app.config.from_pyfile(
        '../config.py', silent=True) or loaded_config

    # Config file pointed to by environment variable
    loaded_config = app.config.from_envvar(
        'WHATHAPPENED_SETTINGS', silent=True) or loaded_config

    if not loaded_config:
        raise ValueError("No external configuration found")

    # Throw out here if there are missing configurations
    if app.config.get("UPLOAD_FOLDER") is None:
        raise ValueError("Missing UPLOAD_FOLDER setting")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as e:
        logger.info(f"Exception occured: {e} ")

    # Init addons
    init_db(app.config['SQLALCHEMY_DATABASE_URI'])

    @app.teardown_appcontext
    def cleanup(resp_or_exc):
        session.remove()

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

    from . import content
    logger.debug("Registering blueprint content")
    app.register_blueprint(content.bp, url_prefix='/content')

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
        from .database import cli  # noqa, Add some commands for database handling.

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

    return app
