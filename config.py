"""App default config."""
import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '.env'))


class Config():
    """Settings to be overridden with env variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'whathappened.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "localhost"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    ADMINS = [os.environ.get('ADMIN_EMAIL') or 'your-email@example.com']
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = False if os.environ.get('FLASK_ENV') != 'development' else True
    MAX_CONTENT_LENGTH = 1024 * 1024  # Max upload size
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.gif']
    UPLOAD_PATH = 'uploads'
