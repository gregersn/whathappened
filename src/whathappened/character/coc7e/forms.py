from wtforms import SelectField
from ..forms import CreateForm as BaseCreateForm

from . import GameTypes


class CreateForm(BaseCreateForm):
    gametype = SelectField(
        "Type",
        choices=GameTypes,
    )
