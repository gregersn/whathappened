from wtforms import Form, StringField, SubmitField
from wtforms.widgets.core import HiddenInput


class CreateInviteForm(Form):
    submit = SubmitField("Create invite")


class DeleteInviteForm(Form):
    id = StringField(widget=HiddenInput())
    submit = SubmitField("Delete share")
