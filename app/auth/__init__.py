import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import UserMixin, current_user, login_user, logout_user

from app import db, login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

from .routes import *

from .models import User
from .forms import LoginForm, RegistrationForm


@login_manager.user_loader
def load_user(id):
    print(f"Loading user {id}")
    return User.query.get(int(id))
