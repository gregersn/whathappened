from whathappened.content.models import Folder
import logging
from flask import (Blueprint, render_template)
from whathappened.auth import login_required, current_user
from whathappened.database import session

bp = Blueprint('profile', __name__)

# from whathappened.character.models import Character  # noqa F401
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
    folders = user_profile.folders  # .filter(Folder.parent_id.__eq__(None))
    return render_template('profile/profile.html.jinja',
                           profile=user_profile,
                           characters=characters,
                           folders=folders)
