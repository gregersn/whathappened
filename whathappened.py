import os

from app import create_app, db, assets
from app.auth import User
from flask_assets import Bundle
from app.profile import UserProfile

app = create_app()

with app.app_context():
    assets.url = app.static_url_path
    assets.config['TYPESCRIPT_CONFIG'] = '--target ES6'
    scss = Bundle('scss/main.scss', 'scss/character.scss', filters='pyscss', output='css/all.css')
    assets.register('scss_all', scss)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'UserProfile': UserProfile}
