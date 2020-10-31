import logging
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, HiddenField
from wtforms import ValidationError, SubmitField, SelectField
from wtforms.validators import DataRequired
import json

from .coc import GameTypes

logger = logging.getLogger(__name__)


class JsonString(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid JSON string'
        self.message = message

    def __call__(self, form, field):
        try:
            json.loads(field.data)
        except Exception:
            logger.error("Could not verify  JSON data", exc_info=True)
            raise ValidationError(self.message)


class ImportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired(), JsonString()])
    conversion = BooleanField('Convert')
    migration = BooleanField('Migrate')
    submit = SubmitField('Import')


class CreateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    gametype = SelectField('Type', choices=GameTypes, )
    submit = SubmitField('Create')


class SkillForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    # value = IntegerField('Value', validators=[DataRequired()])
    submit = SubmitField('Add')


class SubskillForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    parent = HiddenField('Parent', validators=[DataRequired()])
    submit = SubmitField('Add')


class DeleteForm(FlaskForm):
    character_id = HiddenField('CharacterId', validators=[DataRequired()])
    submit = SubmitField('Delete')
