import logging
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash
from app import db
from app.main.forms import CreateInviteForm
from app.auth.models import User
from . import bp
from werkzeug.exceptions import abort

from .models import Campaign
from app.character.models import Character
from app.models import UserProfile
from .forms import CreateForm, InvitePlayerForm, AddCharacterForm
from .forms import JoinCampaignForm, EditForm, RemoveCharacterForm
from .forms import RemovePlayerForm
from app.models import Invite

logger = logging.getLogger(__name__)


@bp.route('/<code>', methods=('GET', 'POST'))
@login_required
def join(code):
    inv = Invite.query.get(code)

    if inv is None or inv.table != Campaign.__tablename__:
        return "Invalid code"

    joinform = JoinCampaignForm()
    if joinform.validate_on_submit():
        campaign = Campaign.query.get(inv.object_id)
        player = current_user.profile
        if player not in campaign.players:
            campaign.players.append(player)
            db.session.commit()

        return redirect(url_for('campaign.view', id=campaign.id))

    flash("Valid code")

    campaign = Campaign.query.get(inv.object_id)
    joinform = JoinCampaignForm(invite_code=code)

    return render_template('campaign/joincampaign.html.jinja',
                           campaign=campaign,
                           joinform=joinform)


@bp.route('/<int:id>', methods=('GET', 'POST'))
@login_required
def view(id):
    invites = None
    campaign = Campaign.query.get(id)
    inviteform = InvitePlayerForm(prefix="inviteform")
    createinviteform = CreateInviteForm(prefix="createinviteform")
    characterform = AddCharacterForm(prefix="characterform")

    is_player = current_user.profile in campaign.players
    is_owner = current_user and current_user.profile.id == campaign.user_id

    logger.debug(f"Viewing campagin {campaign.title}")
    logger.debug(f"There are {campaign.players.count()} players")
    logger.debug(f"There are {campaign.characters.count()} characters")

    if not is_player and not is_owner:
        abort(404, "This is not the campaign your are looking for.")

    if is_owner:
        if createinviteform.submit.data and \
                createinviteform.validate_on_submit():
            invite = Invite(campaign)
            invite.owner_id = campaign.user_id
            db.session.add(invite)
            db.session.commit()

        if inviteform.submit.data and inviteform.validate_on_submit():
            player = (User.query
                      .filter_by(email=inviteform.email.data)
                      .first().profile)
            campaign.players.append(player)
            db.session.commit()
            return redirect(url_for('campaign.view', id=id))

        invites = Invite.query_for(campaign)

    if characterform.submit.data and characterform.validate_on_submit():
        print("Adding character")
        character = characterform.character.data
        if (character not in campaign.characters
                and character.user_id == current_user.profile.id):
            campaign.characters.append(character)
            db.session.commit()
        else:
            flash("Character is already added to campaign")

        return redirect(url_for('campaign.view', id=id))

    createinviteform.submit.label.text = "Create share link."

    return render_template('campaign/campaign.html.jinja',
                           campaign=campaign,
                           invites=invites,
                           inviteform=inviteform,
                           createinviteform=createinviteform,
                           characterform=characterform,
                           editable=is_owner)


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    c = Campaign.query.get(id)
    form = EditForm(obj=c)
    if form.validate_on_submit():
        form.populate_obj(c)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    return render_template('campaign/edit.html.jinja', form=form)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        c = Campaign(title=form.title.data, user_id=current_user.profile.id)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('campaign.view', id=c.id))
    return render_template('campaign/create.html.jinja', form=form)


@bp.route('/<int:id>/removecharacter/<int:characterid>',
          methods=('GET', 'POST'))
@login_required
def remove_character(id, characterid):
    c = Campaign.query.get(id)
    char = Character.query.get(characterid)

    if current_user.profile.id != c.user_id \
            and char.user_id != current_user.profile.id:
        abort(404)
    form = RemoveCharacterForm()

    if form.validate_on_submit():
        c.characters.remove(char)
        db.session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    form.id.data = c.id
    form.character.data = char.id
    return render_template('campaign/removecharacter.html.jinja',
                           character=char,
                           campaign=c,
                           form=form)


@bp.route('/<int:id>/removeplayer/<int:playerid>',
          methods=('GET', 'POST'))
@login_required
def remove_player(id, playerid):
    form = RemovePlayerForm()
    c = Campaign.query.get(id)
    player = UserProfile.query.get(playerid)

    if form.validate_on_submit():
        c.players.remove(player)
        db.session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    form.id.data = c.id
    form.player.data = player.id
    return render_template('campaign/removeplayer.html.jinja',
                           player=player,
                           campaign=c,
                           form=form)
