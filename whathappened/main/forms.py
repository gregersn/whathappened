from wtforms import SubmitField, StringField
from wtforms.widgets.core import HiddenInput

from whathappened.forms.base import BaseForm


class CreateInviteForm(BaseForm):
    submit = SubmitField('Create invite')


class DeleteInviteForm(BaseForm):
    id = StringField(widget=HiddenInput())
    submit = SubmitField('Delete share')
