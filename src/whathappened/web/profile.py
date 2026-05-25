import logging

from litestar import Router, get
from litestar.response.template import Template
from sqlalchemy import desc

from whathappened.core.auth.models import User, UserStatus
from whathappened.core.auth.utils import current_user
from whathappened.core.database import session
from whathappened.web.auth.utils import login_required
from whathappened.web.campaign.forms import InvitePlayerForm
from whathappened.web.utils import render_template

# from whathappened.character.models import Character  # noqa F401
from ..core.database.models import Invite, UserProfile  # noqa F401

logger = logging.getLogger(__name__)


@get(["/", "/index"])
def index() -> Template:
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


# @bp.post("/settings/invite")
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


# @bp.get("/settings")
@login_required
def settings():
    assert current_user is not None
    user_profile = session.get(UserProfile, current_user.id)

    invites = None

    assert user_profile is not None

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


# @bp.post("/settings")
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


profile_router = Router(path="/profile", route_handlers=[index])
