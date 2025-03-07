from pathlib import Path
import click
from flask import current_app
from flask.cli import with_appcontext

from alembic.config import Config
from alembic import command


CONFIG_FILE = Path(current_app.root_path).parent / "migrations/alembic.ini"


@click.group()
def db():
    pass


@db.command()
@click.option(
    "-d",
    "--directory",
    default=None,
    help=('Migration script directory (default is "migrations")'),
)
@click.option("-v", "--verbose", is_flag=True, help="Use more verbose output")
@with_appcontext
def current(directory, verbose):
    """Display the current revision for each database."""
    alembic_cfg = Config(directory or str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    command.current(alembic_cfg, verbose=verbose)


@db.command("history")
@with_appcontext
def history():
    """Show revision history."""
    alembic_cfg = Config(str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    command.history(alembic_cfg)


@db.command("upgrade")
@click.option(
    "-d",
    "--directory",
    default=None,
    help=('Migration script directory (default is "migrations")'),
)
@click.option(
    "--sql",
    is_flag=True,
    help=("Don't emit SQL to database - dump to standard output instead"),
)
@click.option(
    "--tag",
    default=None,
    help=('Arbitrary "tag" name - can be used by custom env.py scripts'),
)
@click.option(
    "-x",
    "--x-arg",
    multiple=True,
    help="Additional arguments consumed by custom env.py scripts",
)
@click.argument("revision", default="head")
@with_appcontext
def upgrade(directory, sql, tag, x_arg, revision):
    """Upgrade to latest revision."""
    alembic_cfg = Config(directory or str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    command.upgrade(alembic_cfg, revision, sql, tag)


@db.command("downgrade")
@click.option(
    "-d",
    "--directory",
    default=None,
    help=('Migration script directory (default is "migrations")'),
)
@click.option(
    "--sql",
    is_flag=True,
    help=("Don't emit SQL to database - dump to standard output instead"),
)
@click.option(
    "--tag",
    default=None,
    help=('Arbitrary "tag" name - can be used by custom env.py scripts'),
)
@click.option(
    "-x",
    "--x-arg",
    multiple=True,
    help="Additional arguments consumed by custom env.py scripts",
)
@click.argument("revision", default="-1")
@with_appcontext
def downgrade(directory, sql=False, tag=None, x_arg=None, revision="-1"):
    """downgrade to previous revision."""
    alembic_cfg = Config(directory or str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    if sql and revision == "-1":
        revision = "head:-1"
    command.downgrade(alembic_cfg, revision, sql, tag)


@db.command("revision")
@click.option(
    "-d",
    "--directory",
    default=None,
    help=('Migration script directory (default is "migrations")'),
)
@click.option("-m", "--message", help=("Migration messasge"), required=True)
@with_appcontext
def revision(directory, message):
    """Create new revision."""
    alembic_cfg = Config(directory or str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    command.revision(alembic_cfg, autogenerate=True, message=message)


@db.command("check")
@click.option(
    "-d",
    "--directory",
    default=None,
    help=('Migration script directory (default is "migrations")'),
)
@with_appcontext
def check(directory):
    """Check if migrations are needed."""
    alembic_cfg = Config(directory or str(CONFIG_FILE))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    command.check(alembic_cfg)


current_app.cli.add_command(db)
