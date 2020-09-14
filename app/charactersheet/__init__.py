from functools import reduce
from flask import Blueprint
from flask_assets import Bundle
from flask_login import current_user
from werkzeug.exceptions import abort

from app import assets

from .models import Character

ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
assets.register('ts_coc', ts_coc)

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)


@bp.context_processor
def character_functions():
    def dict_path(data, path):
        val = reduce(lambda x, y: x.get(y, None), path.split("."), data)
        return val

    def get_skill(data, skillpath, subskill=None):
        path, skill = skillpath.split('#')
        skills = dict_path(data, path)
        for s in skills:
            if s['name'] == skill:
                if subskill is not None and subskill != s.get('subskill',
                                                              'None'):
                    print("Wrong subskill", skill, repr(subskill))
                    continue
                return s

        print("Did not find", skill, subskill)
        return 0

    return dict(dict_path=dict_path, get_skill=get_skill)


def get_character(id, check_author=True):
    character = Character.query.get(id)

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if check_author and character.user_id != current_user.id:
        abort(403)

    return character
