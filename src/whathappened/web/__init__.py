#!/usr/bin/env python3
import logging
import os
from pathlib import Path

from jinja2_webpack import Environment as WebpackEnvironment
from jinja2_webpack.filter import WebpackFilter
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.middleware import DefineMiddleware
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.response import Template
from litestar.static_files.config import StaticFilesConfig, create_static_files_router
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from pelican.plugins.webassets.vendor.webassets import Environment as AssetsEnvironment
from pelican.plugins.webassets.vendor.webassets.bundle import Bundle

from whathappened.config import Config, Settings
from whathappened.web import profile as webprofile
from whathappened.web.auth.middleware import LoginManager
from whathappened.web.email import mail

from ..core.database import init_db, session

try:
    from .._version import __version__
except ModuleNotFoundError:
    __version__ = "unknown"
"""
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # type: ignore  # Not an error
"""
assets_env = AssetsEnvironment(
    directory=Path(__file__).absolute().parent.parent / "static"
)
# csrf = CSRFProtect()

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


from litestar import Litestar, get


@get("/hello")
async def hello_world() -> str:
    return "Hello, world!"


def create_app(test_config: Settings | None = None):
    logger.info("Creating app")

    assets_env._named_bundles = {}

    template_config = TemplateConfig(
        directory="./src/whathappened/templates", engine=JinjaTemplateEngine
    )

    jinja_env = template_config.engine_instance.engine
    jinja_env.globals["whathappened_version"] = __version__
    jinja_env.add_extension("jinja2.ext.do")
    jinja_env.add_extension(
        "pelican.plugins.webassets.vendor.webassets.ext.jinja2.AssetsExtension"
    )
    jinja_env.assets_environment = assets_env  # pyright: ignore[reportGeneralTypeIssues]
    assets_env.url = "/static"

    assets_env.config["TYPESCRIPT_CONFIG"] = "--target ES6"

    scss = Bundle("scss/main.scss", filters="pyscss", output="css/all.css")
    assets_env.register("scss_all", scss)

    css_profile = Bundle(
        "scss/profile.scss", filters="pyscss", output="css/profile.css"
    )
    assets_env.register("scss_profile", css_profile)

    from whathappened.core.auth import models as auth_models
    from whathappened.core.content import models as content_models
    from whathappened.core.database import models

    from . import auth, main

    auth_mw = DefineMiddleware(LoginManager, exclude=["static", "auth"])

    app = Litestar(
        route_handlers=[
            main.routes.main_router,
            auth.routes.auth_router,
            webprofile.profile_router,
        ],
        static_files_config=[
            StaticFilesConfig(
                path="/static", directories=["./src/whathappened/static"], name="static"
            )
        ],
        template_config=template_config,
        middleware=[ServerSideSessionConfig().middleware, auth_mw],
        stores={"sessions": FileStore(path=Path("session_data"))},
    )

    # Init addons
    init_db(Config.SQLALCHEMY_DATABASE_URI, nullpool=test_config is not None)

    return app

    app = Flask(__name__, instance_relative_config=True, static_folder="../static")

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

    app.jinja_env.filters["uberfilter"] = uberfilter

    webpack_manifest = (
        Path(__file__).absolute().parent.parent / "static" / "manifest.json"
    )

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

    from .main import assets

    app.register_blueprint(assets.bp)

    from . import profile

    logger.debug("Registering blueprint profile")
    app.register_blueprint(profile.bp, url_prefix="/profile")

    from .content.blueprints import bp as content_bp

    logger.debug("Registering blueprint content")
    app.register_blueprint(content_bp, url_prefix="/content")

    from .userassets.blueprints import (
        apibp as userassets_apibp,
    )
    from .userassets.blueprints import (
        bp as userassets_bp,
    )

    logger.debug("Registering assets module")
    app.register_blueprint(userassets_bp, url_prefix="/assets")
    app.register_blueprint(userassets_apibp, url_prefix="/api/assets")

    from . import character
    from .character.blueprints import api as character_api
    from .character.blueprints import bp as character_bp

    logger.debug("Registering blueprint character")
    app.register_blueprint(character_bp, url_prefix="/character")
    app.register_blueprint(character_api, url_prefix="/api/character")
    character.register_assets(assets_env)

    from . import campaign
    from .campaign.blueprints import apibp as campaign_apibp
    from .campaign.blueprints import bp as campaign_bp

    app.register_blueprint(campaign_bp, url_prefix="/campaign")
    app.register_blueprint(campaign_apibp, url_prefix="/api/campaign")
    campaign.register_assets(assets_env)

    app.add_url_rule("/", endpoint="profile.index")

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    with app.app_context():
        from .main import (
            database,  # noqa: F401, Add some commands for database handling.
        )

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
