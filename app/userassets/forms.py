from flask_login import current_user
from flask import url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import SubmitField
from wtforms_alchemy.fields import QuerySelectField

from wtforms.fields.core import StringField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired


def available_folders():
    return current_user.profile.assetfolders


def available_assets():
    return current_user.profile.assets


class UploadForm(FlaskForm):
    uploaded = FileField(validators=[FileRequired(),
                                     FileAllowed(['jpg', 'png', 'jpeg', 'gif'],
                                                 'Certain images only')])
    folder_id = HiddenField('FolderId', validators=[DataRequired()])
    submit = SubmitField('Upload')


class AssetSelectForm(FlaskForm):
    asset = QuerySelectField('Asset',
                             query_factory=available_assets,
                             get_label=lambda x: x.path,
                             get_pk=lambda x: url_for('userassets.view',
                                                      fileid=x.id,
                                                      filename=x.filename))
    add = SubmitField('Add')


class NewFolderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    parent_id = HiddenField('Parent', validators=[DataRequired()])
    add = SubmitField('Create folder')


class DeleteAssetForm(FlaskForm):
    id = HiddenField('Asset', validators=[DataRequired()])
    delete = SubmitField('Delete')


class DeleteAssetFolderForm(FlaskForm):
    id = HiddenField('AssetFolder', validators=[DataRequired()])
    delete = SubmitField('Delete')


class MoveAssetForm(FlaskForm):
    id = HiddenField('Asset', validators=[DataRequired()])
    folder = QuerySelectField('Folder',
                              query_factory=available_folders,
                              get_label=lambda x: x.path)
    move = SubmitField('Move')
