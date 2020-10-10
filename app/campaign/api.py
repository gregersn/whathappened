from flask import request, jsonify
from flask_login import current_user
from werkzeug.exceptions import abort
import logging

from app import db

from . import apibp
from .models import Handout

logger = logging.getLogger(__name__)


@apibp.route('/hello/<string:name>')
def hello(name):
    response = {'msg': f"Hello, {name}"}
    return jsonify(response)


@apibp.route('<int:campaignid>/handout/<int:handoutid>/players', methods=('GET', 'POST'))
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
