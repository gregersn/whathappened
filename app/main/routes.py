import logging

from flask import render_template, redirect, url_for
from flask.json import jsonify
from flask_login import current_user
from flask_login.utils import login_required
from werkzeug.exceptions import abort

from app import db
from app.models import Invite


from . import bp
from . import api

from .forms import DeleteInviteForm

logger = logging.getLogger(__name__)


def get_class_by_tablename(tablename):
    for c in db.Model._decl_class_registry.values():
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
        db.session.delete(invite)
        db.session.commit()
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
    db.session.delete(invite)
    db.session.commit()

    return jsonify({'html': 'Deleted'})
