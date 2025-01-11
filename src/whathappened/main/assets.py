"""Assets commands."""

import logging

from flask import Blueprint, current_app
from flask.cli import with_appcontext

from webassets.script import CommandLineEnvironment

bp = Blueprint("assets", __name__)

logger = logging.getLogger(__name__)

_named_bundles = {}


@bp.cli.command("build")
@with_appcontext
def build():
    """Build bundles."""
    cmdenv = CommandLineEnvironment(
        current_app.jinja_env.assets_environment,  # pyright: ignore[reportGeneralTypeIssues]
        logger,
    )
    cmdenv.build()


@bp.cli.command("watch")
@with_appcontext
def watch():
    """Watch bundles for file changes."""
    cmdenv = CommandLineEnvironment(
        current_app.jinja_env.assets_environment,  # pyright: ignore[reportGeneralTypeIssues]
        logger,
    )
    cmdenv.watch()


@bp.cli.command("clean")
@with_appcontext
def clean():
    """Clean bundles."""
    cmdenv = CommandLineEnvironment(
        current_app.jinja_env.assets_environment,  # pyright: ignore[reportGeneralTypeIssues]
        logger,
    )
    cmdenv.clean()
