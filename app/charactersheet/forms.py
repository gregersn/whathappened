from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, ValidationError, SubmitField
from wtforms.validators import DataRequired
import json
from jsoncomment import JsonComment


class JsonString(object):
    def __init__(self, message=None):
        if not message:
            message = u'Field must be a valid JSON string'
        self.message = message

    def __call__(self, form, field):
        try:
            JsonComment(json).loads(field.data)
        except Exception:
            raise ValidationError(self.message)


class ImportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired(), JsonString()])
    submit = SubmitField('Import')
