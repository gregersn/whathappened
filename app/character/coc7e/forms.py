from wtforms import SelectField
from ..forms import CreateForm

from . import GameTypes


class CreateFormCoC(CreateForm):
    gametype = SelectField('Type', choices=GameTypes, )
