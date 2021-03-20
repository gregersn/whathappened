import logging
from flask import (
    Blueprint, render_template
)
from flask_login import login_required, current_user
from app.database import session

bp = Blueprint('profile', __name__, template_folder='templates')

# from app.character.models import Character  # noqa F401
from .models import UserProfile  # noqa F401

logger = logging.getLogger(__name__)


@bp.route('/')
@login_required
def index():

    user_profile = UserProfile.query.get(current_user.id)

    if user_profile is None:
        user_profile = UserProfile(user_id=current_user.id)
        session.add(user_profile)
        session.commit()

    logger.info(f"Showing profile {user_profile.id}")

    characters = user_profile.characters
    return render_template('profile/profile.html.jinja',
                           profile=user_profile,
                           characters=characters)
