"""Campaign related views."""

import logging
from typing import Optional, Text, Union

from flask import render_template, request, redirect, url_for
from flask.views import View
from werkzeug.exceptions import abort
from werkzeug.wrappers import Response
import markdown2

from whathappened.core.database import session
from whathappened.web.userassets.forms import AssetSelectForm
from whathappened.web.auth.utils import login_required, current_user

from .blueprints import bp
from ...core.campaign.models import Campaign, Handout, HandoutGroup
from .forms import HandoutForm, DeleteHandoutForm, HandoutGroupForm

logger = logging.getLogger(__name__)


@bp.app_template_filter("markdown")
def markdown(value: str):
    """Render markdown."""
    return markdown2.markdown(value, extras=["tables", "fenced-code-blocks"])


class HandoutView(View):
    """View class for handouts."""

    def dispatch_request(
        self, campaign_id: int, handout_id: Optional[int] = None
    ) -> Union[Text, Response]:
        logger.debug("Dispatch_request(%s, %s)", campaign_id, handout_id)

        if handout_id is None:
            if request.method == "GET" and handout_id is None:
                return self.list_view(campaign_id)

            if request.method == "POST" and handout_id is None:
                return self.create(campaign_id)
        else:
            if request.method == "POST":
                return self.update(campaign_id, handout_id)

            return self.view(campaign_id, handout_id)

        raise NotImplementedError()

    def create(self, campaign_id: int):
        """Create a handout."""
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
                logger.debug(
                    "Field: %s, value: %s, errors: %s",
                    error,
                    handoutform[error].data,
                    ", ".join(message),
                )

        return redirect(url_for("campaign.handout_view", campaign_id=campaign_id))

    def update(self, campaign_id: int, handout_id: int):
        """Update a handout."""
        logger.debug("Put to handout")
        handout = session.get(Handout, handout_id)

        if handout is None:
            abort(404)

        form = HandoutForm(prefix="handout")
        form.group_id.choices = [
            ("", "(none)"),
        ] + [(g.id, g.name) for g in handout.campaign.handout_groups]  # type: ignore

        if form.submit.data and form.validate_on_submit():
            logger.debug("Form is valid")
            form.populate_obj(handout)
            if not handout.group_id:
                handout.group_id = None
            session.commit()
        else:
            logger.debug("Form did not validate")
            for error, message in form.errors.items():
                logger.debug(
                    "Field: %s, value: %s, errors: %s",
                    error,
                    form[error].data,
                    ", ".join(message),
                )

        return redirect(
            url_for(
                "campaign.handout_view", campaign_id=campaign_id, handout_id=handout.id
            )
        )

    def view(self, campaign_id: int, handout_id: int) -> Text:
        """Show a handout."""
        logger.debug("view(%s, %s)", campaign_id, handout_id)
        handout: Handout = session.get(Handout, handout_id)

        if not handout:
            abort(404)

        if (
            current_user.is_authenticated
            and current_user.profile not in handout.players
            and current_user.profile != handout.campaign.user
        ):
            abort(403)

        editable = False
        if (
            current_user.is_authenticated
            and current_user.profile.id == handout.campaign.user_id
        ):
            editable = True

        if not editable:
            return render_template("campaign/handout_view.html.jinja", handout=handout)

        logger.debug(handout.title)
        logger.debug(handout.status)

        form = HandoutForm(obj=handout, prefix="handout")
        form.group_id.choices = [
            ("", "(none)"),
        ] + [(g.id, g.name) for g in handout.campaign.handout_groups]  # type: ignore

        assetsform = AssetSelectForm(prefix="assetselect")

        return render_template(
            "campaign/handout.html.jinja",
            handout=handout,
            form=form,
            assetsform=assetsform,
            editable=editable,
        )

    @login_required
    def list_view(self, campaign_id: int) -> Text:
        """Show a list of handouts."""
        campaign = session.get(Campaign, campaign_id)

        if campaign is None:
            abort(404)

        is_owner = current_user and current_user.profile.id == campaign.user_id

        handouts = [
            handout
            for handout in campaign.handouts
            if not handout.group
            and (is_owner or current_user.profile in handout.players)
        ]

        groups = {
            group.name: list(
                group.handouts.filter(
                    is_owner or Handout.players.contains(current_user.profile)
                )
            )
            for group in campaign.handout_groups
            if group.handouts
        }

        handoutform = HandoutForm(prefix="handout")
        handoutform.campaign_id.data = campaign.id

        groupform = HandoutGroupForm(prefix="group")
        groupform.campaign_id.data = campaign.id

        return render_template(
            "campaign/handouts.html.jinja",
            editable=is_owner,
            campaign=campaign,
            groups=groups,
            handouts=handouts,
            handoutform=handoutform,
            groupform=groupform,
        )


handout_view = HandoutView.as_view("handout_view")
bp.add_url_rule(
    "/<int:campaign_id>/handouts/",
    defaults={"handout_id": None},
    view_func=handout_view,
    methods=[
        "GET",
    ],
)
bp.add_url_rule(
    "/<int:campaign_id>/handouts/",
    view_func=handout_view,
    methods=[
        "POST",
    ],
)
bp.add_url_rule(
    "/<int:campaign_id>/handouts/<int:handout_id>/",
    view_func=handout_view,
    methods=["GET", "PUT", "DELETE", "POST"],
)


@bp.route(
    "/<int:campaign_id>/handouts/<int:handout_id>/delete", methods=("GET", "POST")
)
def handout_delete(campaign_id: int, handout_id: int):
    """Delete a handout."""
    handout = session.get(Handout, handout_id)

    if handout is None:
        abort(404)

    if current_user.profile.id != handout.campaign.user_id:
        abort(404)

    if handout.campaign_id != campaign_id:
        abort(404)

    form = DeleteHandoutForm()

    if form.validate_on_submit():
        session.delete(handout)
        session.commit()
        return redirect(
            url_for("campaign.handout_view", campaign_id=handout.campaign.id)
        )

    form.campaign_id.data = handout.campaign.id
    form.id.data = handout.id

    return render_template(
        "campaign/delete_handout.html.jinja", form=form, handout=handout
    )
