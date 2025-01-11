import logging
from typing import Optional

from flask import render_template, redirect, url_for, flash, request
from sqlalchemy import and_, or_, desc
from werkzeug.exceptions import abort

from whathappened.main.forms import CreateInviteForm
from whathappened.core.auth.models import User
from whathappened.core.character.models import Character
from whathappened.models import UserProfile, Invite
from whathappened.core.database import session
from whathappened.content.forms import ChooseFolderForm
from whathappened.auth.utils import login_required, current_user

from .blueprints import bp
from ..core.campaign.models import Campaign, CampaignCharacter
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
from ..core.campaign.models import HandoutStatus, NPC, Message

from . import api  # noqa

logger = logging.getLogger(__name__)


@bp.route("/<code>", methods=("GET", "POST"))
@login_required
def join(code: str):
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

        return redirect(url_for("campaign.view", id=campaign.id))

    flash("Valid code")

    campaign = session.get(Campaign, inv.object_id)
    joinform = JoinCampaignForm(invite_code=code)

    return render_template(
        "campaign/joincampaign.html.jinja", campaign=campaign, joinform=joinform
    )


@bp.route("/<int:id>", methods=("GET", "POST"))
@login_required
def view(id: int):
    invites = None
    campaign: Campaign = session.get(Campaign, id)
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

    logger.debug(f"Viewing campagin {campaign.title}")
    logger.debug(f"There are {campaign.players.count()} players")
    logger.debug(f"There are {len(campaign.character_associations)} characters")

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
            return redirect(url_for("campaign.view", id=id))

        invites = Invite.query_for(campaign)

        if npcform.submit.data and npcform.validate_on_submit():
            print("Adding NPC")
            character = npcform.character.data
            npc = NPC(character=character, campaign=campaign)
            session.add(npc)
            session.commit()

            return redirect(url_for("campaign.view", id=id))

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

        return redirect(url_for("campaign.view", id=id))

    createinviteform.submit.label.text = "Create share link."

    handouts = campaign.handouts.filter_by(status=HandoutStatus.visible)
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


@bp.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id: int):
    campaign = session.get(Campaign, id)
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
            return redirect(url_for("campaign.edit", id=campaign.id))

    if form.submit.data and form.validate_on_submit():
        form.populate_obj(campaign)
        session.add(campaign)
        session.commit()
        return redirect(url_for("campaign.view", id=campaign.id))

    if folderform.choose.data and folderform.validate_on_submit():
        print("Folder form submitted!")
        campaign.folder = folderform.folder_id.data
        session.commit()
        return redirect(url_for("campaign.view", id=campaign.id))

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


@bp.route("/<int:id>/export", methods=("GET",))
@login_required
def export(id: int):
    campaign: Campaign = session.get(Campaign, id)
    assert campaign
    return campaign.to_dict(_hide=[])


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        c = Campaign(title=form.title.data, user_id=current_user.profile.id)
        session.add(c)
        session.commit()
        return redirect(url_for("campaign.view", id=c.id))
    return render_template("campaign/create.html.jinja", form=form)


@bp.route("/<int:id>/removecharacter/<int:characterid>", methods=("GET", "POST"))
@login_required
def remove_character(id: int, characterid: int):
    campaign = session.get(Campaign, id)
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
        return redirect(url_for("campaign.view", id=campaign.id))

    form.id.data = campaign.id
    form.character.data = char.id
    return render_template(
        "campaign/removecharacter.html.jinja",
        character=char,
        campaign=campaign,
        form=form,
    )


@bp.route("/<int:id>/association_settings/<int:characterid>", methods=("GET", "POST"))
@login_required
def association_settings(id: int, characterid: int):
    """Character-campaign association settings view."""
    association = session.get(CampaignCharacter, (characterid, id))
    assert association

    if current_user.profile.id != association.character.user_id:
        abort(403)

    form = CampaignAssociationForm(obj=association)

    if form.validate_on_submit():
        form.populate_obj(association)
        session.add(association)
        session.commit()
        return redirect(url_for("campaign.view", id=association.campaign_id))

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


@bp.route("/<int:id>/removenpc/<int:characterid>", methods=("GET", "POST"))
@login_required
def remove_npc(id: int, characterid: int):
    npc = session.get(NPC, characterid)
    assert npc
    form = RemoveCharacterForm()

    if form.validate_on_submit():
        if npc.campaign.id == id:
            session.delete(npc)
            session.commit()
        return redirect(url_for("campaign.view", id=id))

    form.id.data = npc.campaign.id
    form.character.data = npc.character.id

    return render_template(
        "campaign/removecharacter.html.jinja",
        character=npc.character,
        campaign=npc.campaign,
        form=form,
    )


@bp.route("/<int:id>/npc/<int:npcid>", methods=("GET", "POST"))
@login_required
def manage_npc(id: int, npcid: int):
    npc = session.get(NPC, npcid)

    transferform = NPCTransferForm(prefix="npctransfer", npc_id=npcid)

    if npc is None:
        return abort(404)

    if npc.campaign_id != id:
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

            return redirect(url_for("campaign.view", id=campaign.id))

    transferform.player.choices = [
        (p.id, p.user.username) for p in npc.campaign.players
    ]

    return render_template(
        "campaign/managenpc.html.jinja", npc=npc, transferform=transferform
    )


@bp.route("/<int:id>/removeplayer/<int:playerid>", methods=("GET", "POST"))
@login_required
def remove_player(id: int, playerid: int):
    form = RemovePlayerForm()
    campaign = session.get(Campaign, id)
    assert campaign
    player = session.get(UserProfile, playerid)
    assert player

    if form.validate_on_submit():
        campaign.players.remove(player)
        session.commit()
        return redirect(url_for("campaign.view", id=campaign.id))

    form.id.data = campaign.id
    form.player.data = player.id
    return render_template(
        "campaign/removeplayer.html.jinja", player=player, campaign=campaign, form=form
    )


@bp.route("/<int:campaign_id>/player/<int:player_id>/message", methods=("GET", "POST"))
@bp.route("/<int:campaign_id>/message/", methods=("GET", "POST"))
@login_required
def message_player(campaign_id: int, player_id: Optional[int] = None):
    campaign = session.get(Campaign, campaign_id)
    assert campaign
    player = None
    if player_id:
        player = session.get(UserProfile, player_id)

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

        return redirect(url_for("campaign.view", id=campaign.id))

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
