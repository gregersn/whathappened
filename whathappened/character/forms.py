import logging
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms import ValidationError, SubmitField
from wtforms.fields.core import Field
from wtforms.validators import DataRequired
import json

from whathappened.forms.fields import JsonField

logger = logging.getLogger(__name__)


class JsonString(object):
    def __init__(self, message: str = None):
        if not message:
            message = u'Field must be a valid JSON string'
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        try:
            _ = json.loads(field.data)
        except Exception:
            logger.error("Could not verify JSON data", exc_info=True)
            raise ValidationError(self.message)


class ImportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = JsonField('Body', validators=[DataRequired()])
    conversion = BooleanField('Convert')
    migration = BooleanField('Migrate')
    submit = SubmitField('Import')


class CreateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    system = HiddenField('System', validators=[DataRequired()])
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
