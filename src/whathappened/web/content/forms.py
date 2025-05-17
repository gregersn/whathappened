"""Content forms."""

from wtforms.fields.simple import HiddenField, SubmitField
from wtforms import StringField
from wtforms.validators import DataRequired, UUID, Optional
from flask_wtf.form import FlaskForm

from whathappened.web.forms.fields.alchemy import QuerySelectField
from whathappened.web.auth.utils import current_user


class NewFolderForm(FlaskForm):
    """New folder."""

    title = StringField("Title", validators=[DataRequired()])
    owner_id = HiddenField(validators=[DataRequired()])
    # parent_id = QuerySelectField('Parent')
    parent_id = HiddenField(
        validators=[Optional(), UUID()], default=None, filters=[lambda x: x or None]
    )
    add = SubmitField("Add")


def available_folders():
    """Get available folders"""
    return current_user.profile.folders


class ChooseFolderForm(FlaskForm):
    """Choose a folder."""

    folder_id = QuerySelectField(
        query_factory=available_folders, get_label=lambda x: x.title, allow_blank=True
    )
    choose = SubmitField("Choose")
