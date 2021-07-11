from wtforms import SelectField
from ..forms import CreateForm

from .character import GameTypes


class CreateForm(CreateForm):
    gametype = SelectField('Type', choices=GameTypes, )
