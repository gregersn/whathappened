from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile.index'))

    return render_template('main/index.html.jinja')
