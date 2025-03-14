"""Forms for CoC7e."""

from wtforms import SelectField

from whathappened.core.sheets.mechanics.coc7e import GameTypes

from ..forms import CreateForm as BaseCreateForm


class CreateForm(BaseCreateForm):
    """CoC7e create form."""

    gametype = SelectField(
        "Type",
        choices=[(gt, gt) for gt in GameTypes],
    )
