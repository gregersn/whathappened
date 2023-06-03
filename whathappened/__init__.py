#!/usr/bin/env python3
import os
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from webassets import Environment as AssetsEnvironment
from webassets.bundle import Bundle
from jinja2_webpack import Environment as WebpackEnvironment
from jinja2_webpack.filter import WebpackFilter

import logging

from whathappened.config import Config
from whathappened.email import mail

from .database import init_db, session

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # type: ignore  # Not an error
assets_env = AssetsEnvironment(directory=Path(__file__).absolute().parent / 'static')
csrf = CSRFProtect()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s %(message)s', level=logging.DEBUG)
logging.debug('Logger initialized')

logging.getLogger('semver').setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def create_app(test_config=None) -> Flask:
    logger.info("Creating app")

    assets_env._named_bundles = {}
    app = Flask(__name__, instance_relative_config=True)

    # Default settings from config file
    app.config.from_object(Config)

    if test_config is not None:
        app.config.from_object(test_config)

    # Check mandatory settings, and throw if they don't exist
    if app.config.get("UPLOAD_FOLDER") is None:
        raise ValueError("Missing setting for UPLOAD_FOLDER")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as e:
        logger.info(f"Exception occured: {e} ")

    # Init addons
    init_db(app.config['SQLALCHEMY_DATABASE_URI'], nullpool=test_config is not None)

    @app.teardown_appcontext
    def cleanup(resp_or_exc):
        session.remove()

    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    app.jinja_env.add_extension('webassets.ext.jinja2.AssetsExtension')

    webpack_manifest = Path(__file__).absolute().parent / 'static' / 'manifest.json'

    if webpack_manifest.exists():
        webpack_env = WebpackEnvironment(manifest=webpack_manifest, publicRoot="")

        app.jinja_env.filters['webpack'] = WebpackFilter(webpack_env)

    app.jinja_env.assets_environment = assets_env  # pyright: ignore[reportGeneralTypeIssues]

    # Register blueprints
    from . import auth
    logger.debug("Registering blueprint auth")
    app.register_blueprint(auth.bp)

    from . import main
    logger.debug("Registering blueprint main")
    app.register_blueprint(main.bp)

    from . import assets
    app.register_blueprint(assets.bp)

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
    character.register_assets(assets_env)

    from . import campaign
    app.register_blueprint(campaign.bp, url_prefix='/campaign')
    app.register_blueprint(campaign.apibp, url_prefix='/api/campaign')
    campaign.register_assets(assets_env)

    app.add_url_rule('/', endpoint='profile.index')

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    with app.app_context():
        from .database import cli  # noqa, Add some commands for database handling.

        logger.debug("Registering assets")
        assets_env.url = app.static_url_path
        assets_env.config['TYPESCRIPT_CONFIG'] = '--target ES6'

        scss = Bundle('scss/main.scss', filters='pyscss', output='css/all.css')
        assets_env.register('scss_all', scss)

        css_profile = Bundle('scss/profile.scss', filters='pyscss', output='css/profile.css')
        assets_env.register('scss_profile', css_profile)

    return app
