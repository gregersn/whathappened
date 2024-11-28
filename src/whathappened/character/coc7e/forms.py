from wtforms import SelectField

from . import GameTypes

from ..forms import CreateForm as BaseCreateForm


class CreateForm(BaseCreateForm):
    gametype = SelectField(
        "Type",
        choices=GameTypes,
    )
