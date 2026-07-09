import logging

from litestar import Request, Router, get
from litestar.datastructures import State
from litestar.di import Provide
from litestar.response import Redirect
from litestar.response.template import Template
from werkzeug.exceptions import abort

from whathappened.core.auth.models import User
from whathappened.core.auth.utils import current_user
from whathappened.core.database import Base, session
from whathappened.core.database.models import Invite
from whathappened.web.auth.utils import login_required, provide_user

from .forms import DeleteInviteForm

logger = logging.getLogger(__name__)


def get_class_by_tablename(tablename):
    for c in Base.registry._class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
            return c


@get("/")
def index(user: User | None) -> Template | Redirect:
    print(user)
    if user:
        return Redirect("/profile")
    # if current_user.is_authenticated:  # pyright: ignore[reportGeneralTypeIssues]
    #    return redirect(url_for("profile.index"))
    return Template("main/index.html.jinja", context={"current_user": current_user})


@get("/share/<uuid:id>/delete", methods=("GET", "POST"))
@login_required
def invite_delete(id: str) -> Template:
    invite = session.get(Invite, id)
    assert invite is not None
    if current_user.profile.id != invite.owner_id:  # pyright: ignore[reportGeneralTypeIssues]
        logger.debug("Wrong user")
        abort(403)
    form = DeleteInviteForm()
    # if form.validate_on_submit():
    # logger.debug("Delete form validated")
    # session.delete(invite)
    # session.commit()
    # return redirect("/")

    objclass = get_class_by_tablename(invite.table)
    obj = None
    if objclass is not None:
        obj = session.get(objclass, invite.object_id)

    form.id.data = invite.id

    return Template("main/invite_delete.html.jinja", obj=obj, invite=invite, form=form)


"""
@api.route("/invite/<int:id>/delete", methods=("POST",))
@login_required
def api_invite_delete(id):
    invite = session.get(Invite, id)
    assert invite is not None
    if current_user.profile.id != invite.owner_id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(403)
    session.delete(invite)
    session.commit()

    return jsonify({"html": "Deleted"})
"""


main_router = Router(
    path="/",
    route_handlers=[index, invite_delete],
    dependencies={"user": Provide(provide_user)},
)
