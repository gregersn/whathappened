"""Character forms."""

import json
import logging
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms import ValidationError, SubmitField
from wtforms import Field
from wtforms.validators import DataRequired

from whathappened.web.forms.fields import JsonField

logger = logging.getLogger(__name__)


class JsonString(object):
    """Validate string as JSON."""

    def __init__(self, message: Optional[str] = None):
        if not message:
            message = "Field must be a valid JSON string"
        self.message = message

    def __call__(self, _: FlaskForm, field: Field):
        try:
            _ = json.loads(field.data)
        except Exception as exc:
            logger.error("Could not verify JSON data", exc_info=True)
            raise ValidationError(self.message) from exc


class ImportForm(FlaskForm):
    """Character importing form."""

    title = StringField("Title", validators=[DataRequired()])
    body = JsonField("Body", validators=[DataRequired()])
    conversion = BooleanField("Convert")
    migration = BooleanField("Migrate")
    submit = SubmitField("Import")


class EditForm(ImportForm):
    """Edit charcter data form."""

    archived = BooleanField("Archived")


class CreateForm(FlaskForm):
    """Create new character form."""

    title = StringField("Title", validators=[DataRequired()])
    system = HiddenField("System", validators=[DataRequired()])
    submit = SubmitField("Create")


class SkillForm(FlaskForm):
    """Edit skill form."""

    name = StringField("Name", validators=[DataRequired()])
    # value = IntegerField('Value', validators=[DataRequired()])
    submit = SubmitField("Add")


class SubskillForm(FlaskForm):
    """Edit subskill form."""

    name = StringField("Name", validators=[DataRequired()])
    parent = HiddenField("Parent", validators=[DataRequired()])
    submit = SubmitField("Add")


class DeleteForm(FlaskForm):
    """Delete character form."""

    character_id = HiddenField("CharacterId", validators=[DataRequired()])
    submit = SubmitField("Delete")
