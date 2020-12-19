from wtforms import SelectField
from ..forms import CreateForm

from . import GameTypes


class CreateForm(CreateForm):
    gametype = SelectField('Type', choices=GameTypes, )
