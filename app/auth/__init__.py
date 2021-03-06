import logging
from flask import Blueprint, render_template, current_app

from app import login_manager
from app.email import send_mail

bp = Blueprint('auth', __name__, url_prefix='/auth',
               template_folder='templates')

from .models import User  # noqa E402
from .forms import LoginForm, RegistrationForm  # noqa E402


logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(id):
    logger.info(f"Loading user {id}")
    return User.query.get(int(id))


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail('[What Happened?] Reset your password',
              sender=current_app.config['ADMINS'][0],
              recipients=[user.email],
              text_body=render_template('/auth/reset_password.txt',
                                        user=user,
                                        token=token))


from . import routes  # noqa: E402, F401 isort:skip
