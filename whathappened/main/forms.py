from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.widgets.core import HiddenInput


class CreateInviteForm(FlaskForm):
    submit = SubmitField('Create invite')


class DeleteInviteForm(FlaskForm):
    id = StringField(widget=HiddenInput())
    submit = SubmitField('Delete share')
