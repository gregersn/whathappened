import os

from app import create_app, db
from app.auth import User
from app.profile import UserProfile

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'UserProfile': UserProfile}
