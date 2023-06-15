import logging
from typing import Optional
from wtforms import StringField, BooleanField, HiddenField
from wtforms import ValidationError, SubmitField
from wtforms import Field
from wtforms.validators import DataRequired
import json
from whathappened.forms.base import BaseForm

from whathappened.forms.fields import JsonField

logger = logging.getLogger(__name__)


class JsonString(object):

    def __init__(self, message: Optional[str] = None):
        if not message:
            message = u'Field must be a valid JSON string'
        self.message = message

    def __call__(self, form: BaseForm, field: Field):
        try:
            _ = json.loads(field.data)
        except Exception:
            logger.error("Could not verify JSON data", exc_info=True)
            raise ValidationError(self.message)


class ImportForm(BaseForm):
    title = StringField('Title', validators=[DataRequired()])
    body = JsonField('Body', validators=[DataRequired()])
    conversion = BooleanField('Convert')
    migration = BooleanField('Migrate')
    submit = SubmitField('Import')


class CreateForm(BaseForm):
    title = StringField('Title', validators=[DataRequired()])
    system = HiddenField('System', validators=[DataRequired()])
    submit = SubmitField('Create')


class SkillForm(BaseForm):
    name = StringField('Name', validators=[DataRequired()])
    # value = IntegerField('Value', validators=[DataRequired()])
    submit = SubmitField('Add')


class SubskillForm(BaseForm):
    name = StringField('Name', validators=[DataRequired()])
    parent = HiddenField('Parent', validators=[DataRequired()])
    submit = SubmitField('Add')


class DeleteForm(BaseForm):
    character_id = HiddenField('CharacterId', validators=[DataRequired()])
    submit = SubmitField('Delete')
