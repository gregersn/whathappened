"""Campaign routes."""

import logging
from typing import Optional

from flask import render_template, redirect, url_for, flash, request
from sqlalchemy import and_, or_, desc
from werkzeug.exceptions import abort

from whathappened.web.main.forms import CreateInviteForm
from whathappened.core.auth.models import User
from whathappened.core.character.models import Character
from whathappened.core.database.models import UserProfile, Invite
from whathappened.core.database import session
from whathappened.web.content.forms import ChooseFolderForm
from whathappened.web.auth.utils import login_required, current_user

from .blueprints import bp
from ...core.campaign.models import Campaign, CampaignCharacter
from .forms import (
    CreateForm,
    DeleteForm,
    InvitePlayerForm,
    AddCharacterForm,
    AddNPCForm,
)
from .forms import (
    JoinCampaignForm,
    EditForm,
    RemoveCharacterForm,
    CampaignAssociationForm,
)
from .forms import RemovePlayerForm, NPCTransferForm, MessagePlayerForm
from ...core.campaign.models import HandoutStatus, NPC, Message

from . import api  # pylint: disable=unused-import  # noqa: F401

logger = logging.getLogger(__name__)


@bp.route("/<code>", methods=("GET", "POST"))
@login_required
def join(code: str):
    """Join a campaign."""
    inv = session.get(Invite, code)

    if inv is None or inv.table != Campaign.__tablename__:
        return "Invalid code"

    joinform = JoinCampaignForm()
    if joinform.validate_on_submit():
        campaign = session.get(Campaign, inv.object_id)
        assert campaign
        player = current_user.profile
        if player not in campaign.players:
            campaign.players.append(player)
            session.commit()

        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    flash("Valid code")

    campaign = session.get(Campaign, inv.object_id)
    joinform = JoinCampaignForm(invite_code=code)

    return render_template(
        "campaign/joincampaign.html.jinja", campaign=campaign, joinform=joinform
    )


@bp.route("/<int:campaign_id>", methods=("GET", "POST"))
@login_required
def view(campaign_id: int):
    """Show a campaign."""
    invites = None
    campaign: Campaign = session.get(Campaign, campaign_id)
    if not campaign:
        abort(404)

    # Set up forms
    inviteform = InvitePlayerForm(prefix="inviteform")
    createinviteform = CreateInviteForm(prefix="createinviteform")
    characterform = AddCharacterForm(prefix="characterform")
    npcform = AddNPCForm(prefix="npcform")

    messageform = MessagePlayerForm(
        players=[
            (campaign.user_id, "GM"),
        ]
        + [(p.id, p.user.username) for p in campaign.players],
        campaign_id=campaign.id,
        from_id=current_user.profile.id,
    )

    is_player = current_user.profile in campaign.players
    is_owner = current_user and current_user.profile.id == campaign.user_id

    logger.debug("Viewing campagin %s", campaign.title)
    logger.debug("There are %s players", campaign.players.count())
    logger.debug("There are %s characters", len(campaign.character_associations))

    if not is_player and not is_owner:
        abort(404, "This is not the campaign your are looking for.")

    if is_owner:
        if createinviteform.submit.data and createinviteform.validate_on_submit():
            invite = Invite(campaign)
            invite.owner_id = campaign.user_id  # type: ignore
            session.add(invite)
            session.commit()

        if inviteform.submit.data and inviteform.validate_on_submit():
            player = User.query.filter_by(email=inviteform.email.data).first().profile
            campaign.players.append(player)
            session.commit()
            return redirect(url_for("campaign.view", campaign_id=campaign_id))

        invites = Invite.query_for(campaign)

        if npcform.submit.data and npcform.validate_on_submit():
            print("Adding NPC")
            character = npcform.character.data
            npc = NPC(character=character, campaign=campaign)
            session.add(npc)
            session.commit()

            return redirect(url_for("campaign.view", campaign_id=campaign_id))

    if characterform.submit.data and characterform.validate_on_submit():
        print("Adding character")
        character = characterform.character.data
        if (
            character not in campaign.characters
            and character
            and character.user_id == current_user.profile.id
        ):
            campaign_character = CampaignCharacter()
            campaign_character.character = character
            campaign.character_associations.append(campaign_character)
            session.commit()
        else:
            flash("Character is already added to campaign")

        return redirect(url_for("campaign.view", campaign_id=campaign_id))

    createinviteform.submit.label.text = "Create share link."

    handouts = [
        handout
        for handout in campaign.handouts
        if handout.status == HandoutStatus.visible
    ]
    messages = campaign.messages.filter(
        or_(
            Message.from_id == current_user.profile.id,
            Message.to_id == current_user.profile.id,
            Message.to_id.is_(None),
        )
    )

    added_npc_ids = [c.character_id for c in campaign.NPCs]

    npcform.character.query = (
        current_user.profile.characters.filter(Character.id.notin_(added_npc_ids))
        .order_by(desc(Character.folder_id.__eq__(campaign.folder_id)))
        .order_by("title")
    )

    added_character_ids = [c.character_id for c in campaign.character_associations]
    characterform.character.query = (
        current_user.profile.characters.filter(Character.id.notin_(added_character_ids))
        .order_by(desc(Character.folder_id.__eq__(campaign.folder_id)))
        .order_by("title")
    )

    return render_template(
        "campaign/campaign.html.jinja",
        campaign=campaign,
        handouts=handouts,
        invites=invites,
        inviteform=inviteform,
        createinviteform=createinviteform,
        characterform=characterform,
        messages=messages,
        npcform=npcform,
        editable=is_owner,
        messageform=messageform,
    )


@bp.route("/<int:campaign_id>/edit", methods=("GET", "POST"))
def edit(campaign_id: int):
    """Edit campaign."""
    campaign = session.get(Campaign, campaign_id)
    assert campaign
    form = EditForm(obj=campaign, prefix="campaign_edit")
    folderform = ChooseFolderForm(prefix="choose_folder")
    deleteform = DeleteForm(obj=campaign, prefix="delete_campaign")

    if deleteform.submit.data and deleteform.validate_on_submit():
        if deleteform.confirm.data == "CONFIRM":
            print("DELETE CAMPAIGN!")
            invites = Invite.query_for(campaign)
            if invites:
                invites.delete()

            session.delete(campaign)
            session.commit()
            return redirect("/")
        else:
            return redirect(url_for("campaign.edit", campaign_id=campaign.id))

    if form.submit.data and form.validate_on_submit():
        form.populate_obj(campaign)
        session.add(campaign)
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    if folderform.choose.data and folderform.validate_on_submit():
        print("Folder form submitted!")
        campaign.folder = folderform.folder_id.data
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    folderform.folder_id.data = campaign.folder
    invites = Invite.query_for(campaign).count()
    return render_template(
        "campaign/edit.html.jinja",
        form=form,
        folderform=folderform,
        deleteform=deleteform,
        campaign=campaign,
        invites=invites,
    )


@bp.route("/<int:campaign_id>/export", methods=("GET",))
@login_required
def export(campaign_id: int):
    """Export campaign."""
    campaign: Campaign = session.get(Campaign, campaign_id)
    assert campaign
    return campaign.to_dict(_hide=[])


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a campaign."""
    form = CreateForm()
    if form.validate_on_submit():
        c = Campaign(title=form.title.data, user_id=current_user.profile.id)
        session.add(c)
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=c.id))
    return render_template("campaign/create.html.jinja", form=form)


@bp.route(
    "/<int:campaign_id>/removecharacter/<int:characterid>", methods=("GET", "POST")
)
@login_required
def remove_character(campaign_id: int, characterid: int):
    """Remove character from campaign."""
    campaign = session.get(Campaign, campaign_id)
    assert campaign
    char = session.get(Character, characterid)
    assert char
    if (
        current_user.profile.id != campaign.user_id
        and char.user_id != current_user.profile.id
    ):
        abort(404)
    form = RemoveCharacterForm()

    if form.validate_on_submit():
        session.delete(session.get(CampaignCharacter, (char.id, campaign.id)))
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    form.id.data = campaign.id
    form.character.data = char.id
    return render_template(
        "campaign/removecharacter.html.jinja",
        character=char,
        campaign=campaign,
        form=form,
    )


@bp.route(
    "/<int:campaign_id>/association_settings/<int:characterid>", methods=("GET", "POST")
)
@login_required
def association_settings(campaign_id: int, characterid: int):
    """Character-campaign association settings view."""
    association = session.get(CampaignCharacter, (characterid, campaign_id))
    assert association

    if current_user.profile.id != association.character.user_id:
        abort(403)

    form = CampaignAssociationForm(obj=association)

    if form.validate_on_submit():
        form.populate_obj(association)
        session.add(association)
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=association.campaign_id))

    form.campaign_id.data = association.campaign_id
    form.character_id.data = association.character_id

    logger.debug(association)

    return render_template(
        "campaign/campaign_association.html.jinja",
        association=association,
        character=association.character,
        campaign=association.campaign,
        form=form,
    )


@bp.route("/<int:campaign_id>/removenpc/<int:characterid>", methods=("GET", "POST"))
@login_required
def remove_npc(campaign_id: int, characterid: int):
    """Remove NPC from campaign."""
    npc = session.get(NPC, characterid)
    assert npc
    form = RemoveCharacterForm()

    if form.validate_on_submit():
        if npc.campaign.id == campaign_id:
            session.delete(npc)
            session.commit()
        return redirect(url_for("campaign.view", campaign_id=campaign_id))

    form.id.data = npc.campaign.id
    form.character.data = npc.character.id

    return render_template(
        "campaign/removecharacter.html.jinja",
        character=npc.character,
        campaign=npc.campaign,
        form=form,
    )


@bp.route("/<int:campaign_id>/npc/<int:npcid>", methods=("GET", "POST"))
@login_required
def manage_npc(campaign_id: int, npcid: int):
    """Manage NPCs in campaign."""
    npc = session.get(NPC, npcid)

    transferform = NPCTransferForm(prefix="npctransfer", npc_id=npcid)

    if npc is None:
        return abort(404)

    if npc.campaign_id != campaign_id:
        return abort(404)

    if current_user.profile != npc.campaign.user:
        return abort(404)

    if transferform.submit.data:
        if transferform.validate_on_submit():
            player = session.get(UserProfile, transferform.player.data)
            assert player
            campaign = npc.campaign

            # Create a copy of the character
            new_character = Character(
                title=npc.character.title, body=npc.character.body, user_id=player.id
            )

            session.add(new_character)

            # Add the character to the campaign
            campaign.characters.append(new_character)

            # Remove the NPC
            session.delete(npc)

            # Commit changes
            session.commit()

            return redirect(url_for("campaign.view", campaign_id=campaign.id))

    transferform.player.choices = [
        (p.id, p.user.username) for p in npc.campaign.players
    ]

    return render_template(
        "campaign/managenpc.html.jinja", npc=npc, transferform=transferform
    )


@bp.route("/<int:campaign_id>/removeplayer/<int:playerid>", methods=("GET", "POST"))
@login_required
def remove_player(campaign_id: int, playerid: int):
    """Remove player from campaign."""
    form = RemovePlayerForm()
    campaign = session.get(Campaign, campaign_id)
    assert campaign
    player = session.get(UserProfile, playerid)
    assert player

    if form.validate_on_submit():
        campaign.players.remove(player)
        session.commit()
        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    form.id.data = campaign.id
    form.player.data = player.id
    return render_template(
        "campaign/removeplayer.html.jinja", player=player, campaign=campaign, form=form
    )


@bp.route("/<int:campaign_id>/player/<int:player_id>/message", methods=("GET", "POST"))
@bp.route("/<int:campaign_id>/message/", methods=("GET", "POST"))
@login_required
def message_player(campaign_id: int, player_id: Optional[int] = None):
    """Send message to player."""
    campaign = session.get(Campaign, campaign_id)

    if campaign is None:
        abort(404)

    player = None

    if player_id:
        player = session.get(UserProfile, player_id)

    form = MessagePlayerForm()

    if form.validate_on_submit():
        if form.message.data is not None:
            flash(form.message.data)
        logger.debug(request.form)

        message = Message()
        form.populate_obj(message)
        if not form.to_id.data:
            message.to_id = None  # type: ignore

        session.add(message)
        session.commit()

        return redirect(url_for("campaign.view", campaign_id=campaign.id))

    form.campaign_id.data = campaign.id
    form.to_id.data = player_id
    form.from_id.data = campaign.user_id

    messages = campaign.messages.filter(
        or_(
            and_(
                Message.to_id == player_id, Message.from_id == current_user.profile.id
            ),
            and_(
                Message.to_id == current_user.profile.id, Message.from_id == player_id
            ),
        )
    )
    return render_template(
        "campaign/message_player.html.jinja",
        player=player,
        campaign=campaign,
        form=form,
        messages=messages,
    )