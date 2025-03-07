from flask import url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import SubmitField

from wtforms import StringField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired

from whathappened.web.auth.utils import current_user
from whathappened.web.forms.fields import QuerySelectField
from ...core.userassets.models import Asset


def available_folders():
    return current_user.profile.assetfolders


def available_assets():
    return (
        Asset.query.filter(Asset.owner == current_user.profile)
        .order_by(Asset.folder_id)
        .order_by(Asset.filename)
    )


VALID_FILE_EXTENSIONS = ["jpg", "png", "jpeg", "gif", "svg", "glb"]


class UploadForm(FlaskForm):
    uploaded = FileField(
        validators=[
            FileRequired(),
            FileAllowed(VALID_FILE_EXTENSIONS, "Certain images only"),
        ]
    )
    folder_id = HiddenField("FolderId", validators=[DataRequired()])
    submit = SubmitField("Upload")


class AssetSelectForm(FlaskForm):
    asset = QuerySelectField(
        "Asset",
        query_factory=available_assets,
        get_label=lambda x: "/".join(x.path.parts[2:]),
        get_pk=lambda x: url_for("userassets.view", fileid=x.id, filename=x.filename),
    )
    add = SubmitField("Add")


class NewFolderForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    parent_id = HiddenField("Parent", validators=[DataRequired()])
    add = SubmitField("Create folder")


class DeleteAssetForm(FlaskForm):
    id = HiddenField("Asset", validators=[DataRequired()])
    delete = SubmitField("Delete")


class DeleteAssetFolderForm(FlaskForm):
    id = HiddenField("AssetFolder", validators=[DataRequired()])
    delete = SubmitField("Delete")


class MoveAssetForm(FlaskForm):
    id = HiddenField("Asset", validators=[DataRequired()])
    folder = QuerySelectField(
        "Folder", query_factory=available_folders, get_label=lambda x: x.path
    )
    move = SubmitField("Move")
