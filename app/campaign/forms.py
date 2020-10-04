from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms import SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.core import IntegerField
from wtforms.validators import DataRequired, Email
from flask_login import current_user
from wtforms.widgets.core import HiddenInput, TextArea


class CreateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create')


class EditForm(CreateForm):
    id = IntegerField(widget=HiddenInput())
    description = StringField('Description', widget=TextArea())
    submit = SubmitField('Save')


class InvitePlayerForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),  Email()])
    submit = SubmitField('Invite')


def available_characters():
    return current_user.profile.characters


class AddCharacterForm(FlaskForm):
    character = QuerySelectField(query_factory=available_characters,
                                 get_label=lambda x: x.title)
    submit = SubmitField('Add character')


class RemoveCharacterForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    character = IntegerField(widget=HiddenInput())
    submit = SubmitField('Remove character')


class RemovePlayerForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    player = IntegerField(widget=HiddenInput())
    submit = SubmitField('Remove player')


class JoinCampaignForm(FlaskForm):
    invite_code = HiddenField('Invite', validators=[DataRequired()])
    submit = SubmitField('Join campaign')
