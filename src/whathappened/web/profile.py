import logging
from sqlalchemy import desc
from flask import Blueprint, render_template, request
from whathappened.web.auth.utils import login_required, current_user
from whathappened.core.database import session

bp = Blueprint("profile", __name__, template_folder="../templates")

# from whathappened.character.models import Character  # noqa F401
from ..core.database.models import UserProfile  # noqa F401

logger = logging.getLogger(__name__)


@bp.route("/")
@login_required
def index():
    assert current_user is not None
    user_profile = session.get(UserProfile, current_user.id)  # type: ignore

    if user_profile is None:
        user_profile = UserProfile(user_id=current_user.id)  # type: ignore
        session.add(user_profile)
        session.commit()

    logger.info("Showing profile %s", user_profile.id)

    characters = user_profile.characters.filter_by(archived=False).order_by(
        desc("timestamp")
    )
    folders = user_profile.folders  # .filter(Folder.parent_id.__eq__(None))
    return render_template(
        "profile/profile.html.jinja",
        profile=user_profile,
        characters=characters,
        folders=folders,
    )


@bp.get("/settings")
@login_required
def settings():
    assert current_user is not None
    user_profile = session.get(UserProfile, current_user.id)

    return render_template(
        "profile/settings.html.jinja", profile=user_profile, user=current_user
    )


@bp.post("/settings")
@login_required
def settings_post():
    assert current_user is not None
    user_profile = session.get(UserProfile, current_user.id)

    for field_change in request.get_json():
        if hasattr(user_profile, field_change["field_name"]):
            setattr(
                user_profile, field_change["field_name"], str(field_change["value"])
            )
    session.commit()

    return "Good"
