import logging
from sqlalchemy import desc
from flask import Blueprint, current_app, flash, redirect, render_template, request
from whathappened.core.auth.models import User, UserStatus
from whathappened.web.auth.utils import login_required, current_user
from whathappened.core.database import session
from whathappened.web.campaign.forms import InvitePlayerForm

bp = Blueprint("profile", __name__, template_folder="../templates")

# from whathappened.character.models import Character  # noqa F401
from ..core.database.models import Invite, UserProfile  # noqa F401

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


@bp.post("/settings/invite")
@login_required
def settings_invite_post():
    assert current_user is not None
    form = InvitePlayerForm()

    if form.validate_on_submit():
        user_profile = session.get(UserProfile, current_user.id)
        assert user_profile
        invited_user = User(
            username=form.email.data, email=form.email.data, status=UserStatus.invited
        )
        session.add(invited_user)
        session.commit()

        user_invite = Invite(invited_user)
        user_invite.owner_id = user_profile.id
        session.add(user_invite)

        session.commit()
        flash("User is invited.")

    return redirect("/profile/settings")


@bp.get("/settings")
@login_required
def settings():
    assert current_user is not None
    user_profile = session.get(UserProfile, current_user.id)

    invites = None

    if current_app.config.get("REQUIRE_INVITE"):
        invitations = (
            session.query(Invite, User)
            .filter(Invite.owner_id == user_profile.id)
            .filter(Invite.table == User.__tablename__)
            .filter(User.id == Invite.object_id)
            .all()
        )
        invites = {
            "form": InvitePlayerForm(),
            "invitations": invitations,
        }

    return render_template(
        "profile/settings.html.jinja",
        profile=user_profile,
        user=current_user,
        invites=invites,
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
