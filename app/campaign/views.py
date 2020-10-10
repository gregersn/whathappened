from typing import Text
from flask import render_template, request, redirect, url_for
from flask_login import current_user
from flask.views import View
from werkzeug.exceptions import abort
import logging

import markdown2

from app import db
from . import bp

from .models import Campaign, Handout
from .forms import HandoutForm, DeleteHandoutForm, RevealHandout

logger = logging.getLogger(__name__)


@bp.app_template_filter('markdown')
def markdown(value):
    return markdown2.markdown(value)


class HandoutView(View):
    def dispatch_request(self, campaign_id: int, handout_id=None) -> Text:
        logger.debug(f"dispatch_request({campaign_id}, {handout_id})")

        if request.method == 'GET' and handout_id is None:
            return self.list_view(campaign_id)

        if request.method == 'POST' and handout_id is None:
            return self.create(campaign_id)

        if request.method == 'POST':
            return self.update(campaign_id, handout_id)

        return self.view(campaign_id, handout_id)

    def create(self, campaign_id):
        logger.debug("Posting handout")
        form = HandoutForm()
        if form.validate_on_submit():
            logger.debug("Store handout")
            handout = Handout()
            form.populate_obj(handout)
            db.session.add(handout)
            db.session.commit()
        else:
            logger.debug("Form did not validate")
            for error, message in form.errors.items():
                logger.debug(f"Field: {error}, value: {form[error].data}, errors: {', '.join(message)}")

        return redirect(url_for('campaign.handout_view',
                                campaign_id=campaign_id))

    def update(self, campaign_id, handout_id):
        logger.debug("Put to handout")
        handout = Handout.query.get(handout_id)
        form = HandoutForm()
        available_players = handout.campaign.players
        form.players.query = available_players

        if form.validate_on_submit():
            logger.debug("Form is valid")
            form.populate_obj(handout)
            db.session.commit()
        else:
            logger.debug("Form did not validate")
            for error, message in form.errors.items():
                logger.debug(f"Field: {error}, value: {form[error].data}, errors: {', '.join(message)}")

        return redirect(url_for('campaign.handout_view',
                                campaign_id=campaign_id,
                                handout_id=handout.id))

    def view(self, campaign_id, handout_id=None) -> Text:
        logger.debug(f"view({campaign_id}, {handout_id})")
        handout = Handout.query.get(handout_id)

        if current_user.profile not in handout.players and current_user.profile != handout.campaign.user:
            abort(403)

        editable = False
        if current_user.profile.id == handout.campaign.user_id:
            editable = True

        if not editable:
            return render_template('campaign/handout_view.html.jinja',
                                   handout=handout)

        logger.debug(handout.title)
        logger.debug(handout.status)

        available_players = handout.campaign.players

        form = HandoutForm(obj=handout)
        form.players.query = available_players

        return render_template('campaign/handout.html.jinja',
                               handout=handout,
                               form=form,
                               editable=editable)

    def list_view(self, campaign_id: int) -> Text:
        campaign = Campaign.query.get(campaign_id)
        is_owner = current_user and current_user.profile.id == campaign.user_id
        handouts = campaign.handouts
        logger.debug(handouts)
        form = HandoutForm()
        form.campaign_id.data = campaign.id

        return render_template('campaign/handouts.html.jinja',
                               editable=is_owner,
                               campaign=campaign,
                               handouts=handouts,
                               form=form)


handout_view = HandoutView.as_view('handout_view')
bp.add_url_rule('/<int:campaign_id>/handouts/',
                defaults={'handout_id': None},
                view_func=handout_view,
                methods=['GET', ])
bp.add_url_rule('/<int:campaign_id>/handouts/',
                view_func=handout_view,
                methods=['POST', ])
bp.add_url_rule('/<int:campaign_id>/handouts/<int:handout_id>/',
                view_func=handout_view,
                methods=['GET', 'PUT', 'DELETE', 'POST'])


@bp.route('/<int:campaign_id>/handouts/<int:handout_id>/delete',
          methods=('GET', 'POST'))
def handout_delete(campaign_id, handout_id):
    """Delete a handout."""
    handout = Handout.query.get(handout_id)

    if current_user.profile.id != handout.campaign.user_id:
        abort(404)

    form = DeleteHandoutForm()

    if form.validate_on_submit():
        db.session.delete(handout)
        db.session.commit()
        return redirect(url_for('campaign.handout_view',
                                campaign_id=handout.campaign.id))

    form.campaign_id.data = handout.campaign.id
    form.handout_id.data = handout.id

    return render_template('campaign/delete_handout.html.jinja',
                           form=form,
                           handout=handout)
