from wtforms import SelectField

from whathappened.core.sheets.mechanics.coc7e import GameTypes

from ..forms import CreateForm as BaseCreateForm


class CreateForm(BaseCreateForm):
    gametype = SelectField(
        "Type",
        choices=GameTypes,
    )
