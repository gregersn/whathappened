import os

from app import create_app, db

from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)