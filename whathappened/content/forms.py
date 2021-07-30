from flask_login import current_user
from wtforms.fields.simple import HiddenField, SubmitField
from flask_wtf.form import FlaskForm
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired, UUID, Optional

from whathappened.forms.fields.alchemy import QuerySelectField


class NewFolderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    owner_id = HiddenField(validators=[DataRequired()])
    # parent_id = QuerySelectField('Parent')
    parent_id = HiddenField(
        validators=[Optional(), UUID()],
        default=None,
        filters=[lambda x: x or None])
    add = SubmitField('Add')


def available_folders():
    return current_user.profile.folders


class ChooseFolderForm(FlaskForm):
    folder_id = QuerySelectField(
        query_factory=available_folders,
        get_label=lambda x: x.title,
        allow_blank=True)
    choose = SubmitField('Choose')
