"""Campaign API functions."""

import json
import hashlib
import logging
from datetime import datetime

from flask import request, jsonify
from sqlalchemy import or_
from werkzeug.exceptions import abort

from whathappened.web.auth.utils import login_required, current_user
from whathappened.core.database import session

from .blueprints import apibp
from ...core.campaign.models import Handout, Campaign, HandoutStatus, NPC, Message

logger = logging.getLogger(__name__)


@apibp.route("/hello/<string:name>")
def hello(name: str):
    """Test function."""
    response = {"msg": f"Hello, {name}"}
    return jsonify(response)


@apibp.route("<int:campaignid>/handouts/", methods=("GET",))
def handouts(campaignid: int):
    """Get handouts."""
    if not current_user.is_authenticated:
        abort(403)

    campaign = session.get(Campaign, campaignid)
    if campaign is None:
        abort(404)

    if current_user.profile not in campaign.players:
        abort(403)

    active_handouts = [
        handout
        for handout in campaign.handouts
        if handout.status == HandoutStatus.visible
        and current_user.profile in handout.players
    ]

    handouts_dict = [handout.to_dict(show=["url"]) for handout in active_handouts]

    sha = hashlib.sha256()
    sha.update(json.dumps(handouts_dict).encode("utf-8"))

    return jsonify({"sha": sha.hexdigest(), "handouts": handouts_dict})


@apibp.route("<int:campaignid>/player/<int:playerid>/message", methods=("GET", "POST"))
def message_player(campaignid: int, playerid: int):
    """Send message to player."""
    logger.debug("Got a message in the post")
    logger.debug(request.form)
    return jsonify({"status": "ok"})


@apibp.route("<int:campaignid>/messages", methods=("GET",))
@login_required
def messages(campaignid: int):
    """Get messages."""
    after = int(request.args.get("after", "0"), 10)
    logger.debug("Get all messages for campaign %s after %s", campaignid, after)
    campaign = session.get(Campaign, campaignid)

    if campaign is None:
        abort(404)

    found_messages = (
        campaign.messages.filter(
            or_(
                Message.from_id == current_user.profile.id,
                Message.to_id == current_user.profile.id,
                Message.to_id.is_(None),
            )
        )
        .filter(Message.timestamp > datetime.fromtimestamp(after))
        .order_by("timestamp")
    )

    message_list = [m.to_dict() for m in found_messages]
    return jsonify(message_list)


@apibp.route(
    "<int:campaignid>/handout/<int:handoutid>/players", methods=("GET", "POST")
)
def handout_players(campaignid: int, handoutid: int):
    """Get player handout."""
    if not current_user.is_authenticated:
        abort(403)

    handout = session.get(Handout, handoutid)
    if handout is None:
        abort(404)

    if handout.campaign.id != campaignid:
        abort(404)

    if current_user.profile != handout.campaign.user:
        abort(403)

    if request.method == "POST":
        data = request.get_json()
        assert data is not None

        player = handout.campaign.players_by_id.get(data["player_id"], None)
        if player is not None:
            if data["state"]:
                if player not in handout.players:
                    logger.debug("Adding player %s to %s", player, handout)
                    handout.players.append(player)
            else:
                if player in handout.players:
                    logger.debug("Removing player %s to %s", player, handout)
                    handout.players.remove(player)

            session.commit()

        logger.debug(data)

    response = {
        "players": {
            p.user.username: p in handout.players for p in handout.campaign.players
        }
    }
    return jsonify(response)


@apibp.route("<int:campaignid>/npcs/", methods=("GET", "POST"))
@login_required
def npcs(campaignid: int):
    """Get NPCs."""
    campaign = session.get(Campaign, campaignid)

    if campaign is None:
        abort(404)

    active_npcs = [
        {
            "name": npc.character.name,
            "age": npc.character.age,
            "description": npc.character.description,
            "portrait": "data:image/jpg;base64, " + npc.character.portrait
            if npc.character.portrait
            else "",
        }
        for npc in campaign.NPCs
        if npc.visible
    ]
    response = {"npcs": active_npcs}
    return jsonify(response)


@apibp.route("<int:campaignid>/npc/<int:npcid>", methods=("GET", "POST"))
@login_required
def npc_visibility(npcid: int, campaignid: int):
    """Control NPC visibility."""
    if not current_user.is_authenticated:
        abort(403)

    npc = session.get(NPC, npcid)
    if npc is None:
        abort(404)

    if npc.campaign.id != campaignid:
        abort(404)

    if current_user.profile != npc.campaign.user:
        abort(403)

    if request.method == "POST":
        data = request.get_json()
        assert data is not None
        logger.debug(data)
        if data["visibility"]:
            logger.debug("Showing NPC %s", npc.character.title)
            npc.visible = True
        else:
            logger.debug("Hiding NPC %s", npc.character.title)
            npc.visible = False

        session.commit()

        logger.debug(data)

    response = {"npc": npcid, "campaign": campaignid, "visibility": npc.visible}
    return jsonify(response)
