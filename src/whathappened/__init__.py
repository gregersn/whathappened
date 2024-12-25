#!/usr/bin/env python3
from pathlib import Path
import os
import logging

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from webassets import Environment as AssetsEnvironment
from webassets.bundle import Bundle
from jinja2_webpack import Environment as WebpackEnvironment
from jinja2_webpack.filter import WebpackFilter


from whathappened.config import Config
from whathappened.email import mail

from .database import init_db, session

try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = "unknown"

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # type: ignore  # Not an error
assets_env = AssetsEnvironment(directory=Path(__file__).absolute().parent / "static")
csrf = CSRFProtect()

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s %(message)s",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)
logging.debug("Logger initialized")

logging.getLogger("semver").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


FILTERS = {
    "parenthesize": lambda x: f"({x})",
    "": lambda x: x,
}


def uberfilter(inp: str, filter: str = ""):
    fun = FILTERS.get(filter, None)
    if fun:
        return fun(inp)
    return inp


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
    instance_path = Path(app.instance_path)
    if not instance_path.exists():
        instance_path.mkdir(parents=True)

    # Init addons
    init_db(app.config["SQLALCHEMY_DATABASE_URI"], nullpool=test_config is not None)

    @app.teardown_appcontext
    def cleanup(resp_or_exc):
        session.remove()

    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    app.jinja_env.globals["whathappened_version"] = __version__
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("webassets.ext.jinja2.AssetsExtension")

    app.jinja_env.filters["uberfilter"] = uberfilter

    webpack_manifest = Path(__file__).absolute().parent / "static" / "manifest.json"

    if webpack_manifest.exists():
        logger.debug("Loading webpack manifest")
        webpack_env = WebpackEnvironment(manifest=webpack_manifest, publicRoot="")

        app.jinja_env.filters["webpack"] = WebpackFilter(webpack_env)

    app.jinja_env.assets_environment = assets_env  # pyright: ignore[reportGeneralTypeIssues]

    # Register blueprints
    from .auth.blueprints import bp as auth_bp

    logger.debug("Registering blueprint auth")
    app.register_blueprint(auth_bp)

    from . import main

    logger.debug("Registering blueprint main")
    app.register_blueprint(main.bp)

    from . import assets

    app.register_blueprint(assets.bp)

    from . import profile

    logger.debug("Registering blueprint profile")
    app.register_blueprint(profile.bp, url_prefix="/profile")

    from .content.blueprints import bp as content_bp

    logger.debug("Registering blueprint content")
    app.register_blueprint(content_bp, url_prefix="/content")

    from .userassets.blueprints import bp as userassets_bp, apibp as userassets_apibp

    logger.debug("Registering assets module")
    app.register_blueprint(userassets_bp, url_prefix="/assets")
    app.register_blueprint(userassets_apibp, url_prefix="/api/assets")

    from .character.blueprints import bp as character_bp, api as character_api
    from . import character

    logger.debug("Registering blueprint character")
    app.register_blueprint(character_bp, url_prefix="/character")
    app.register_blueprint(character_api, url_prefix="/api/character")
    character.register_assets(assets_env)

    from .campaign.blueprints import bp as campaign_bp, apibp as campaign_apibp
    from . import campaign

    app.register_blueprint(campaign_bp, url_prefix="/campaign")
    app.register_blueprint(campaign_apibp, url_prefix="/api/campaign")
    campaign.register_assets(assets_env)

    app.add_url_rule("/", endpoint="profile.index")

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    with app.app_context():
        from .database import cli  # noqa: F401, Add some commands for database handling.

        logger.debug("Registering assets")
        assets_env.url = app.static_url_path
        assets_env.config["TYPESCRIPT_CONFIG"] = "--target ES6"

        scss = Bundle("scss/main.scss", filters="pyscss", output="css/all.css")
        assets_env.register("scss_all", scss)

        css_profile = Bundle(
            "scss/profile.scss", filters="pyscss", output="css/profile.css"
        )
        assets_env.register("scss_profile", css_profile)

    return app
