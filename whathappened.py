from app import create_app, db
from app.auth import User
from app.profile import UserProfile

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app.charactersheet.models import Character
    return {'db': db,
            'User': User,
            'UserProfile': UserProfile,
            'Character': Character
        }
