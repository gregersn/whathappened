import logging
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, HiddenField
from wtforms import ValidationError, SubmitField
from wtforms.validators import DataRequired
import json

logger = logging.getLogger(__name__)


class JsonString(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid JSON string'
        self.message = message

    def __call__(self, form, field):
        try:
            _ = json.loads(field.data)
        except Exception:
            logger.error("Could not verify JSON data", exc_info=True)
            raise ValidationError(self.message)


class JsonField(TextAreaField):
    def _value(self):
        return json.dumps(self.data, indent=4) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError('This field is not valid JSON')
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError("Invalid JSON")


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
