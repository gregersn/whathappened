from functools import reduce
from flask import Blueprint
from flask_assets import Bundle

from app import assets

ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
assets.register('ts_coc', ts_coc)

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)


@bp.context_processor
def character_functions():
    def dict_path(data, path):
        val = reduce(lambda x, y: x.get(y, {}) if x is not None else {},
                     path.split("."),
                     data)
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


from . import routes  # noqa: F401 isort:skip
