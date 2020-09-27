from flask_migrate import Migrate, upgrade

from app import create_app, db

from app.auth import User
from app.profile import UserProfile
from app.charactersheet.models import Character

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'UserProfile': UserProfile,
            'Character': Character
        }
