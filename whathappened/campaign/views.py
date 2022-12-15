from typing import Text, Union
from flask import render_template, request, redirect, url_for
from flask.views import View
from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import logging

import markdown2

from . import bp

from .models import Campaign, Handout, HandoutGroup
from .forms import HandoutForm, DeleteHandoutForm, HandoutGroupForm
from whathappened.userassets.forms import AssetSelectForm
from whathappened.database import session
from whathappened.auth import login_required, current_user

logger = logging.getLogger(__name__)


@bp.app_template_filter('markdown')
def markdown(value: str):
    return markdown2.markdown(value, extras=["tables", "fenced-code-blocks"])


class HandoutView(View):

    def dispatch_request(self, campaign_id: int, handout_id: int) -> Union[Text, Response]:
        logger.debug(f"dispatch_request({campaign_id}, {handout_id})")

        if request.method == 'GET' and handout_id is None:
            return self.list_view(campaign_id)

        if request.method == 'POST' and handout_id is None:
            return self.create(campaign_id)

        if request.method == 'POST':
            if handout_id is not None:
                return self.update(campaign_id, handout_id)

        return self.view(campaign_id, handout_id)

    def create(self, campaign_id: int):
        logger.debug("Posting handout")
        handoutform = HandoutForm(prefix="handout")
        groupform = HandoutGroupForm(prefix="group")
        if handoutform.submit.data and handoutform.validate_on_submit():
            logger.debug("Store handout")
            handout = Handout()
            handoutform.populate_obj(handout)
            if not handout.group_id:
                handout.group_id = None  # type: ignore

            session.add(handout)
            session.commit()
        elif groupform.submit.data and groupform.validate_on_submit():
            logger.debug("Create handout group")
            group = HandoutGroup()
            groupform.populate_obj(group)
            session.add(group)
            session.commit()
        else:
            logger.debug("Form did not validate")
            for error, message in handoutform.errors.items():
                logger.debug(f"Field: {error}, "
                             f"value: {handoutform[error].data}, "
                             f"errors: {', '.join(message)}")

        return redirect(url_for('campaign.handout_view', campaign_id=campaign_id))

    def update(self, campaign_id: int, handout_id: int):
        logger.debug("Put to handout")
        handout = Handout.query.get(handout_id)
        form = HandoutForm(prefix="handout")
        form.group_id.choices = [('', '(none)'), ] \
            + [(g.id, g.name)
                for g in handout.campaign.handout_groups]

        if form.submit.data and form.validate_on_submit():
            logger.debug("Form is valid")
            form.populate_obj(handout)
            if not handout.group_id:
                handout.group_id = None
            session.commit()
        else:
            logger.debug("Form did not validate")
            for error, message in form.errors.items():
                logger.debug(f"Field: {error}, "
                             f"value: {form[error].data}, "
                             f"errors: {', '.join(message)}")

        return redirect(url_for('campaign.handout_view', campaign_id=campaign_id, handout_id=handout.id))

    def view(self, campaign_id: int, handout_id: int) -> Text:
        logger.debug(f"view({campaign_id}, {handout_id})")
        handout: Handout = Handout.query.get(handout_id)

        if not handout:
            abort(404)

        if current_user.is_authenticated \
            and current_user.profile not in handout.players \
                and current_user.profile != handout.campaign.user:  # pyright: ignore[reportGeneralTypeIssues]
            abort(403)

        editable = False
        if current_user.is_authenticated \
                and current_user.profile.id == handout.campaign.user_id:  # pyright: ignore[reportGeneralTypeIssues]
            editable = True

        if not editable:
            return render_template('campaign/handout_view.html.jinja', handout=handout)

        logger.debug(handout.title)
        logger.debug(handout.status)

        form = HandoutForm(obj=handout, prefix="handout")
        form.group_id.choices = [('', '(none)'), ] \
            + [(g.id, g.name)
               for g in handout.campaign.handout_groups]

        assetsform = AssetSelectForm(prefix="assetselect")

        return render_template('campaign/handout.html.jinja',
                               handout=handout,
                               form=form,
                               assetsform=assetsform,
                               editable=editable)

    @login_required
    def list_view(self, campaign_id: int) -> Text:
        campaign = Campaign.query.get(campaign_id)
        is_owner = current_user and current_user.profile.id == campaign.user_id  # pyright: ignore[reportGeneralTypeIssues]
        handouts = campaign.handouts.filter(~Handout.group.has()) \
            .filter(is_owner or Handout.players.contains(current_user.profile))  # pyright: ignore[reportGeneralTypeIssues]

        groups = {
            group.name: list(group.handouts.filter(
                is_owner or Handout.players.contains(current_user.profile)))  # pyright: ignore[reportGeneralTypeIssues]
            for group in campaign.handout_groups
        }

        handoutform = HandoutForm(prefix="handout")
        handoutform.campaign_id.data = campaign.id

        groupform = HandoutGroupForm(prefix="group")
        groupform.campaign_id.data = campaign.id

        return render_template('campaign/handouts.html.jinja',
                               editable=is_owner,
                               campaign=campaign,
                               groups=groups,
                               handouts=handouts,
                               handoutform=handoutform,
                               groupform=groupform)


handout_view = HandoutView.as_view('handout_view')
bp.add_url_rule('/<int:campaign_id>/handouts/',
                defaults={'handout_id': None},
                view_func=handout_view,
                methods=[
                    'GET',
                ])
bp.add_url_rule('/<int:campaign_id>/handouts/', view_func=handout_view, methods=[
    'POST',
])
bp.add_url_rule('/<int:campaign_id>/handouts/<int:handout_id>/',
                view_func=handout_view,
                methods=['GET', 'PUT', 'DELETE', 'POST'])


@bp.route('/<int:campaign_id>/handouts/<int:handout_id>/delete', methods=('GET', 'POST'))
def handout_delete(campaign_id: int, handout_id: int):
    """Delete a handout."""
    handout = Handout.query.get(handout_id)

    if current_user.profile.id != handout.campaign.user_id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(404)

    form = DeleteHandoutForm()

    if form.validate_on_submit():
        session.delete(handout)
        session.commit()
        return redirect(url_for('campaign.handout_view', campaign_id=handout.campaign.id))

    form.campaign_id.data = handout.campaign.id
    form.id.data = handout.id

    return render_template('campaign/delete_handout.html.jinja', form=form, handout=handout)
