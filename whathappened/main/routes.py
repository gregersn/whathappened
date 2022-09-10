import logging





from werkzeug.exceptions import abort

from whathappened.models import Invite
from whathappened.database import session, Base
from whathappened.auth import login_required, current_user

from . import bp
from . import api

from .forms import DeleteInviteForm

logger = logging.getLogger(__name__)


def get_class_by_tablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile.index'))

    return render_template('main/index.html.jinja')


@bp.route('/share/<uuid:id>/delete', methods=('GET', 'POST'))
@login_required
def invite_delete(id):
    invite = Invite.query.get(id)
    if current_user.profile.id != invite.owner_id:
        logger.debug("Wrong user")
        abort(403)
    form = DeleteInviteForm()
    if form.validate_on_submit():
        logger.debug("Delete form validated")
        session.delete(invite)
        session.commit()
        return redirect('/')

    objclass = get_class_by_tablename(invite.table)
    obj = None
    if objclass is not None:
        obj = objclass.query.get(invite.object_id)

    form.id.data = invite.id

    return render_template('main/invite_delete.html.jinja',
                           obj=obj,
                           invite=invite,
                           form=form)


@api.route('/invite/<int:id>/delete', methods=('POST', ))
@login_required
def api_invite_delete(id):
    invite = Invite.query.get(id)
    if current_user.profile.id != invite.owner_id:
        abort(403)
    session.delete(invite)
    session.commit()

    return jsonify({'html': 'Deleted'})
