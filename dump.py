#!/usr/bin/env python3
import os
import click

from app.auth.models import User
from app.models import LogEntry, UserProfile

from app.database import init_db, db, session

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@click.group()
def cli():
    pass


@cli.command()
def dump():
    print("Dumping database")
    database_uri = 'sqlite:///' + \
        os.path.join(BASEDIR, 'instance', 'whathappened.sqlite')
    init_db(database_uri)

    log = UserProfile.query.all()
    for l in log:
        print(l.to_dict())


if __name__ == '__main__':
    cli()

