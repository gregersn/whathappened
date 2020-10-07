from app import create_app, db

from app.auth.models import User, Role, UserRoles
from app.profile import UserProfile
from app.character.models import Character

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'UserProfile': UserProfile,
            'Character': Character,
            'Role': Role,
            'UserRoles': UserRoles
          }
