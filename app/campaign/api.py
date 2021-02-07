import json
import hashlib
from datetime import datetime
from flask import request, jsonify
from flask_login import current_user
from flask_login.utils import login_required
from sqlalchemy import or_

from werkzeug.exceptions import abort
import logging

from app import db

from . import apibp
from .models import Handout, Campaign, HandoutStatus, NPC, Message

logger = logging.getLogger(__name__)


@apibp.route('/hello/<string:name>')
def hello(name):
    response = {'msg': f"Hello, {name}"}
    return jsonify(response)


@apibp.route('<int:campaignid>/handouts/', methods=('GET', ))
def handouts(campaignid: int):
    if not current_user.is_authenticated:
        abort(403)

    campaign = Campaign.query.get(campaignid)
    if current_user.profile not in campaign.players:
        abort(403)

    handouts = campaign.handouts.filter_by(status=HandoutStatus.visible) \
        .filter(Handout.players.contains(current_user.profile))

    handouts_dict = [handout.to_dict() for handout in handouts]

    sha = hashlib.sha256()
    sha.update(json.dumps(handouts_dict).encode('utf-8'))

    return jsonify({'sha': sha.hexdigest(), 'handouts': handouts_dict})


@apibp.route('<int:campaignid>/player/<int:playerid>/message', methods=('GET', 'POST'))
def message_player(campaignid: int, playerid: int):
    logger.debug("Got a message in the post")
    logger.debug(request.form)
    return jsonify({'status': 'ok'})


@apibp.route('<int:campaignid>/messages', methods=('GET', ))
@login_required
def messages(campaignid: int):
    after = int(request.args.get('after'), 10)
    logger.debug(f"Get all messages for campaign {campaignid} after {after}")
    campaign = Campaign.query.get(campaignid)
    messages = campaign.messages.filter(or_(
                                    Message.from_id == current_user.profile.id,
                                    Message.to_id == current_user.profile.id,
                                    Message.to_id.is_(None))).filter(Message.timestamp > datetime.fromtimestamp(after)).order_by('timestamp')

    message_list = [m.to_dict() for m in messages]
    return jsonify(message_list)


@apibp.route('<int:campaignid>/handout/<int:handoutid>/players',
             methods=('GET', 'POST'))
def handout_players(campaignid: int, handoutid: int):
    if not current_user.is_authenticated:
        abort(403)

    handout = Handout.query.get(handoutid)
    if handout is None:
        abort(404)

    if handout.campaign.id != campaignid:
        abort(404)

    if current_user.profile != handout.campaign.user:
        abort(403)

    if request.method == 'POST':
        data = request.get_json()
        player = handout.campaign.players_by_id.get(data['player_id'], None)
        if player is not None:
            if data['state']:
                if player not in handout.players:
                    logger.debug(f"Adding player {player} to {handout}")
                    handout.players.append(player)
            else:
                if player in handout.players:
                    logger.debug(f"Removing player {player} to {handout}")
                    handout.players.remove(player)

            db.session.commit()

        logger.debug(data)

    response = {
        'players': {
            p.user.username: p in handout.players for p in handout.campaign.players
        }
    }
    return jsonify(response)


@apibp.route('<int:campaignid>/npcs/', methods=('GET', 'POST'))
@login_required
def npcs(campaignid: int):
    campaign = Campaign.query.get(campaignid)

    if campaign is None:
        abort(404)

    npcs = [{'name': npc.character.name,
             'age': npc.character.age,
             'description': npc.character.description,
             'portrait': "data:image/jpg;base64, " + npc.character.portrait } for npc in campaign.NPCs.filter(NPC.visible).all()]
    response = {'npcs': npcs}
    return jsonify(response)


@apibp.route('<int:campaignid>/npc/<int:npcid>',
             methods=('GET', 'POST'))
@login_required
def npc_visibility(npcid: int, campaignid: int):
    if not current_user.is_authenticated:
        abort(403)

    npc = NPC.query.get(npcid)
    if npc is None:
        abort(404)

    if npc.campaign.id != campaignid:
        abort(404)

    if current_user.profile != npc.campaign.user:
        abort(403)

    if request.method == 'POST':
        data = request.get_json()
        logger.debug(data)
        if data['visibility']:
            logger.debug(f"Showing NPC {npc.character.title}")
            npc.visible = True
        else:
            logger.debug(f"Hiding NPC {npc.character.title}")
            npc.visible = False

        db.session.commit()

        logger.debug(data)

    response = {
        'npc': npcid, 'campaign': campaignid, 'visibility': npc.visible
    }
    return jsonify(response)
