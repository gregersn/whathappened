"""App default config."""
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config():
    """Settings to be overridden with env variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'whathappened.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "localhost"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025, 10)
    ADMINS = ['your-email@example.com']
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True
