from functools import reduce
from flask import Blueprint
from flask_assets import Bundle

from app import assets

ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
assets.register('ts_coc', ts_coc)

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)

from . import routes  # noqa: F401 isort:skip
