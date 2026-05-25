from wtforms import Form, StringField
from wtforms.fields.simple import HiddenField, SubmitField
from wtforms.validators import UUID, DataRequired, Optional

from whathappened.web.forms.fields.alchemy import QuerySelectField


class NewFolderForm(Form):
    title = StringField("Title", validators=[DataRequired()])
    owner_id = HiddenField(validators=[DataRequired()])
    # parent_id = QuerySelectField('Parent')
    parent_id = HiddenField(
        validators=[Optional(), UUID()], default=None, filters=[lambda x: x or None]
    )
    add = SubmitField("Add")


def available_folders():
    return current_user.profile.folders  # pyright: ignore[reportGeneralTypeIssues]


class ChooseFolderForm(Form):
    folder_id = QuerySelectField(
        query_factory=available_folders, get_label=lambda x: x.title, allow_blank=True
    )
    choose = SubmitField("Choose")
