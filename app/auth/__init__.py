import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from flask_login import UserMixin, current_user, login_user, logout_user

from app import db, login_manager
from app.email import send_mail

bp = Blueprint('auth', __name__, url_prefix='/auth')

from .models import User
from .forms import LoginForm, RegistrationForm


@login_manager.user_loader
def load_user(id):
    print(f"Loading user {id}")
    return User.query.get(int(id))

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail('[What Happened?] Reset your password',
             sender=current_app.config['ADMINS'][0],
             recipients=[user.email],
             text_body=render_template('/auth/reset_password.txt', user=user, token=token))

from .routes import *
