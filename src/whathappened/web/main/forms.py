"""Main web forms."""

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.widgets.core import HiddenInput


class CreateInviteForm(FlaskForm):
    """Create invitation."""

    submit = SubmitField("Create invite")


class DeleteInviteForm(FlaskForm):
    """Delete invitation."""

    id = StringField(widget=HiddenInput())
    submit = SubmitField("Delete share")
