import logging

from flask import render_template, redirect, url_for
from flask.json import jsonify
from werkzeug.exceptions import abort

from whathappened.core.database.models import Invite
from whathappened.core.database import session, Base
from whathappened.web.auth.utils import login_required, current_user

from .blueprints import bp, api

from .forms import DeleteInviteForm

logger = logging.getLogger(__name__)


def get_class_by_tablename(tablename):
    for c in Base.registry._class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
            return c


@bp.route("/")
def index():
    if current_user.is_authenticated:  # pyright: ignore[reportGeneralTypeIssues]
        return redirect(url_for("profile.index"))

    return render_template("main/index.html.jinja")


@bp.route("/share/<uuid:id>/delete", methods=("GET", "POST"))
@login_required
def invite_delete(id):
    invite = session.get(Invite, id)
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


@api.route("/invite/<int:id>/delete", methods=("POST",))
@login_required
def api_invite_delete(id):
    invite = session.get(Invite, id)
    if current_user.profile.id != invite.owner_id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(403)
    session.delete(invite)
    session.commit()

    return jsonify({"html": "Deleted"})
