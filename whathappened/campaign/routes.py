import logging
from flask import render_template, redirect, url_for, flash, request
from whathappened.main.forms import CreateInviteForm
from whathappened.auth.models import User
from . import bp
from werkzeug.exceptions import abort

from .models import Campaign
from whathappened.database.models import Character
from whathappened.models import UserProfile
from .forms import CreateForm, InvitePlayerForm, AddCharacterForm, AddNPCForm
from .forms import JoinCampaignForm, EditForm, RemoveCharacterForm
from .forms import RemovePlayerForm, NPCTransferForm, MessagePlayerForm
from .models import HandoutStatus, NPC, Message
from whathappened.models import Invite
from sqlalchemy import and_, or_
from whathappened.database import session
from whathappened.content.forms import ChooseFolderForm
from whathappened.auth import login_required, current_user

from . import api  # noqa

logger = logging.getLogger(__name__)


@bp.route('/<code>', methods=('GET', 'POST'))
@login_required
def join(code: str):
    inv = Invite.query.get(code)

    if inv is None or inv.table != Campaign.__tablename__:
        return "Invalid code"

    joinform = JoinCampaignForm()
    if joinform.validate_on_submit():
        campaign = Campaign.query.get(inv.object_id)
        player = current_user.profile
        if player not in campaign.players:
            campaign.players.append(player)
            session.commit()

        return redirect(url_for('campaign.view', id=campaign.id))

    flash("Valid code")

    campaign = Campaign.query.get(inv.object_id)
    joinform = JoinCampaignForm(invite_code=code)

    return render_template('campaign/joincampaign.html.jinja', campaign=campaign, joinform=joinform)


@bp.route('/<int:id>', methods=('GET', 'POST'))
@login_required
def view(id: int):
    invites = None
    campaign: Campaign = Campaign.query.get(id)

    # Set up forms
    inviteform = InvitePlayerForm(prefix="inviteform")
    createinviteform = CreateInviteForm(prefix="createinviteform")
    characterform = AddCharacterForm(prefix="characterform")
    npcform = AddNPCForm(prefix="npcform")

    messageform = MessagePlayerForm(players=[
        (campaign.user_id, "GM"),
    ] + [(p.id, p.user.username) for p in campaign.players],
                                    campaign_id=campaign.id,
                                    from_id=current_user.profile.id)

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
            invite.owner_id = campaign.user_id  # type: ignore
            session.add(invite)
            session.commit()

        if inviteform.submit.data and inviteform.validate_on_submit():
            player = (User.query.filter_by(email=inviteform.email.data).first().profile)
            campaign.players.append(player)
            session.commit()
            return redirect(url_for('campaign.view', id=id))

        invites = Invite.query_for(campaign)

        if npcform.submit.data and npcform.validate_on_submit():
            print("Adding NPC")
            character = npcform.character.data
            npc = NPC(character=character, campaign=campaign)
            session.add(npc)
            session.commit()

            return redirect(url_for('campaign.view', id=id))

    if characterform.submit.data and characterform.validate_on_submit():
        print("Adding character")
        character = characterform.character.data
        if (character not in campaign.characters and character.user_id == current_user.profile.id):
            campaign.characters.append(character)
            session.commit()
        else:
            flash("Character is already added to campaign")

        return redirect(url_for('campaign.view', id=id))

    createinviteform.submit.label.text = "Create share link."

    handouts = campaign.handouts.filter_by(status=HandoutStatus.visible)
    messages = campaign.messages.filter(
        or_(Message.from_id == current_user.profile.id, Message.to_id == current_user.profile.id, Message.to_id.is_(None)))

    added_npc_ids = [c.character_id for c in campaign.NPCs]

    npcform.character.query = current_user.profile.characters.filter(
        Character.id.notin_(added_npc_ids)).\
        order_by(
            Character.folder_id.__eq__(campaign.folder_id).desc()).\
        order_by('title')

    added_character_ids = [c.id for c in campaign.characters]
    characterform.character.query = current_user.profile.characters.\
        filter(Character.id.notin_(added_character_ids)).\
        order_by(Character.folder_id.__eq__(campaign.folder_id).desc()).\
        order_by('title')

    return render_template('campaign/campaign.html.jinja',
                           campaign=campaign,
                           handouts=handouts,
                           invites=invites,
                           inviteform=inviteform,
                           createinviteform=createinviteform,
                           characterform=characterform,
                           messages=messages,
                           npcform=npcform,
                           editable=is_owner,
                           messageform=messageform)


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id: int):
    c = Campaign.query.get(id)
    form = EditForm(obj=c, prefix="campaign_edit")
    folderform = ChooseFolderForm(prefix="choose_folder")

    if form.submit.data and form.validate_on_submit():
        form.populate_obj(c)
        session.add(c)
        session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    if folderform.choose.data and folderform.validate_on_submit():
        print("Folder form submitted!")
        c.folder = folderform.folder_id.data
        session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    folderform.folder_id.data = c.folder

    return render_template('campaign/edit.html.jinja', form=form, folderform=folderform)


@bp.route("/<int:id>/export", methods=("GET", ))
@login_required
def export(id: int):
    c: Campaign = Campaign.query.get(id)
    return c.to_dict(_hide=[])


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        c = Campaign(title=form.title.data, user_id=current_user.profile.id)
        session.add(c)
        session.commit()
        return redirect(url_for('campaign.view', id=c.id))
    return render_template('campaign/create.html.jinja', form=form)


@bp.route('/<int:id>/removecharacter/<int:characterid>', methods=('GET', 'POST'))
@login_required
def remove_character(id: int, characterid: int):
    c = Campaign.query.get(id)
    char = Character.query.get(characterid)

    if current_user.profile.id != c.user_id \
            and char.user_id != current_user.profile.id:
        abort(404)
    form = RemoveCharacterForm()

    if form.validate_on_submit():
        c.characters.remove(char)
        session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    form.id.data = c.id
    form.character.data = char.id
    return render_template('campaign/removecharacter.html.jinja', character=char, campaign=c, form=form)


@bp.route('/<int:id>/removenpc/<int:characterid>', methods=('GET', 'POST'))
@login_required
def remove_npc(id: int, characterid: int):
    npc = NPC.query.get(characterid)

    form = RemoveCharacterForm()

    if form.validate_on_submit():
        if npc.campaign.id == id:
            session.delete(npc)
            session.commit()
        return redirect(url_for('campaign.view', id=id))

    form.id.data = npc.campaign.id
    form.character.data = npc.character.id

    return render_template('campaign/removecharacter.html.jinja', character=npc.character, campaign=npc.campaign, form=form)


@bp.route('/<int:id>/npc/<int:npcid>', methods=('GET', 'POST'))
@login_required
def manage_npc(id: int, npcid: int):
    npc = NPC.query.get(npcid)

    transferform = NPCTransferForm(prefix="npctransfer", npc_id=npcid)

    if npc is None:
        return abort(404)

    if npc.campaign_id != id:
        return abort(404)

    if current_user.profile != npc.campaign.user:
        return abort(404)

    if transferform.submit.data:
        if transferform.validate_on_submit():
            player = UserProfile.query.get(transferform.player.data)
            campaign = npc.campaign

            # Create a copy of the character
            new_character = Character(title=npc.character.title, body=npc.character.body, user_id=player.id)

            session.add(new_character)

            # Add the character to the campaign
            campaign.characters.append(new_character)

            # Remove the NPC
            session.delete(npc)

            # Commit changes
            session.commit()

            return redirect(url_for('campaign.view', id=campaign.id))

    transferform.player.choices = [(p.id, p.user.username) for p in npc.campaign.players]

    return render_template('campaign/managenpc.html.jinja', npc=npc, transferform=transferform)


@bp.route('/<int:id>/removeplayer/<int:playerid>', methods=('GET', 'POST'))
@login_required
def remove_player(id: int, playerid: int):
    form = RemovePlayerForm()
    c = Campaign.query.get(id)
    player = UserProfile.query.get(playerid)

    if form.validate_on_submit():
        c.players.remove(player)
        session.commit()
        return redirect(url_for('campaign.view', id=c.id))

    form.id.data = c.id
    form.player.data = player.id
    return render_template('campaign/removeplayer.html.jinja', player=player, campaign=c, form=form)


@bp.route('/<int:campaign_id>/player/<int:player_id>/message', methods=('GET', 'POST'))
@bp.route('/<int:campaign_id>/message/', methods=('GET', 'POST'))
@login_required
def message_player(campaign_id: int, player_id: int = None):
    c = Campaign.query.get(campaign_id)
    player = None
    if player_id:
        player = UserProfile.query.get(player_id)

    form = MessagePlayerForm()

    if form.validate_on_submit():
        flash(form.message.data)
        logger.debug(request.form)

        message = Message()
        form.populate_obj(message)
        if not form.to_id.data:
            message.to_id = None  # type: ignore

        session.add(message)
        session.commit()

        return redirect(url_for('campaign.view', id=c.id))

    form.campaign_id.data = c.id
    form.to_id.data = player_id
    form.from_id.data = c.user_id

    messages = c.messages.filter(
        or_(and_(Message.to_id == player_id, Message.from_id == current_user.profile.id),
            and_(Message.to_id == current_user.profile.id, Message.from_id == player_id)))
    return render_template('campaign/message_player.html.jinja', player=player, campaign=c, form=form, messages=messages)
