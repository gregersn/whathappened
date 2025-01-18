"""Main web routes."""

import logging

from flask import render_template, redirect, url_for
from flask.json import jsonify
from werkzeug.exceptions import abort

from whathappened.core.database.models import Invite
from whathappened.core.database import session
from whathappened.core.database.utils import get_class_by_tablename
from whathappened.web.auth.utils import login_required, current_user

from .blueprints import bp, api

from .forms import DeleteInviteForm

logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """Front page or user profile."""
    if current_user.is_authenticated:  # pyright: ignore[reportGeneralTypeIssues]
        return redirect(url_for("profile.index"))

    return render_template("main/index.html.jinja")


@bp.route("/share/<uuid:invite_id>/delete", methods=("GET", "POST"))
@login_required
def invite_delete(invite_id):
    """Delete an invite."""
    invite = session.get(Invite, invite_id)

    if invite is None:
        abort(404)

    if current_user.profile.id != invite.owner_id:  # pyright: ignore[reportGeneralTypeIssues]
        logger.debug("Wrong user")
        abort(403)
    form = DeleteInviteForm()
    if form.validate_on_submit():
        logger.debug("Delete form validated")
        session.delete(invite)
        session.commit()
        return redirect("/")

    objclass = get_class_by_tablename(invite.table)
    obj = None
    if objclass is not None:
        obj = session.get(objclass, invite.object_id)

    form.id.data = invite.id

    return render_template(
        "main/invite_delete.html.jinja", obj=obj, invite=invite, form=form
    )


@api.route("/invite/<int:invite_id>/delete", methods=("POST",))
@login_required
def api_invite_delete(invite_id: int):
    """Delete an invite."""
    invite = session.get(Invite, invite_id)

    if invite is None:
        abort(404)

    if current_user.profile.id != invite.owner_id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(403)
    session.delete(invite)
    session.commit()

    return jsonify({"html": "Deleted"})
