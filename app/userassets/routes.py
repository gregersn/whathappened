import os
from pathlib import Path
import logging
from flask import render_template, current_app, flash
from flask import request, redirect, url_for
from flask.helpers import send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from app import db
from . import bp
from .forms import DeleteAssetFolderForm, DeleteAssetForm, UploadForm, NewFolderForm, MoveAssetForm

from .models import Asset, AssetFolder

logger = logging.getLogger(__name__)


@bp.route('/<uuid:folder_id>/')
@bp.route('/')
@login_required
def index(folder_id=None):
    if not current_user.profile.assetfolders:
        rootfolder = AssetFolder(title='assets', owner=current_user.profile)
        db.session.add(rootfolder)
        db.session.commit()

    if folder_id is not None:
        folder = AssetFolder.query.get(folder_id)
    else:
        folder = current_user.profile.assetfolders \
                    .filter(AssetFolder.parent_id.__eq__(None)).first()

    form = UploadForm(folder_id=folder.id, prefix="fileupload")
    folderform = NewFolderForm(parent_id=folder.id, prefix="newfolderform")
    deletefolderform = DeleteAssetFolderForm(id=folder.id,
                                             prefix="deletefolderform")

    return render_template('assets.html.jinja',
                           form=form,
                           folderform=folderform,
                           deletefolderform=deletefolderform,
                           folder=folder)


@bp.route('/folder/<uuid:folder_id>/', methods=['POST', ])
@bp.route('/folder/', methods=['POST', ])
@login_required
def create_folder(folder_id=None):
    folderform = NewFolderForm(prefix="newfolderform")
    if folderform.validate_on_submit():
        logger.debug("Create a new folder")
        folder = AssetFolder(parent_id=folderform.parent_id.data, title=folderform.title.data, owner=current_user.profile)
        db.session.add(folder)
        db.session.commit()
    return redirect(url_for('userassets.index', folder_id=folder_id))


@bp.route('/folder/<uuid:id>/delete', methods=['POST', ])
@login_required
def delete_folder(id=None):
    deletefolderform = DeleteAssetFolderForm(prefix="deletefolderform")
    folder = AssetFolder.query.get(id)

    if not folder.owner == current_user.profile:
        logger.debug("Not deleting folder for other person")
        abort(403)

    if folder.parent is None:
        logger.debug("Can't delete top folder")
        abort(403)

    if deletefolderform.validate_on_submit():
        logger.debug("Delete an empty folder")
        parent_id = folder.parent.id

        if str(folder.id) != deletefolderform.id.data:
            logger.debug(f"Wrong ids specified {folder.id} and {deletefolderform.id.data}")
            abort(403)

        if folder.files:
            logger.debug("Folder contains files")
            abort(403)

        db.session.delete(folder)
        db.session.commit()
        return redirect(url_for('userassets.index', folder_id=parent_id))

    return redirect(url_for('userassets.index', folder_id=id))


@bp.route('/<uuid:folder_id>/', methods=['POST', ])
@bp.route('/', methods=['POST', ])
@login_required
def upload_file(folder_id=None):
    form = UploadForm(prefix='fileupload')
    if form.validate_on_submit():
        fileobject = form.uploaded.data
        folder = AssetFolder.query.get(form.folder_id.data)

        if folder.owner != current_user.profile:
            abort(403)

        filename = secure_filename(fileobject.filename)
        Path(folder.system_path).mkdir(parents=True,
                                       exist_ok=True)
        fileobject.save(os.path.join(folder.system_path, filename))

        asset = Asset(filename=fileobject.filename,
                      folder=folder,
                      owner=current_user.profile)
        db.session.add(asset)
        db.session.commit()

    return redirect(url_for('userassets.index', folder_id=folder_id))


@bp.route('/view/<uuid:fileid>/<string:filename>')
@login_required
def view(fileid, filename):
    userasset = Asset.query.get(fileid)
    if filename != userasset.filename:
        abort(404)

    filepath = userasset.folder.get_path()
    assetname = secure_filename(userasset.filename)
    logger.debug(f"Sending file from {filepath}, {assetname}")

    full_dir = os.path.join("..", userasset.folder.system_path)
    return send_from_directory(full_dir, assetname)


@bp.route('/edit/<uuid:fileid>/<string:filename>')
@login_required
def edit(fileid, filename):
    userasset = Asset.query.get(fileid)
    if filename != userasset.filename:
        abort(404)

    deleteform = DeleteAssetForm(id=userasset.id, prefix="deleteasset")
    moveform = MoveAssetForm(id=userasset.id,
                             prefix="moveasset",
                             folder=userasset.folder)

    return render_template('edit.html.jinja',
                           asset=userasset,
                           deleteform=deleteform,
                           moveform=moveform)


@bp.route('/edit/<uuid:fileid>/<string:filename>/delete', methods=['POST', ])
@login_required
def delete(fileid, filename):
    logger.debug("Delete asset")
    asset = Asset.query.get(fileid)
    form = DeleteAssetForm(prefix="deleteasset")
    if form.validate_on_submit():
        if asset.owner != current_user.profile:
            abort(403)
        flash("You just deleted an asset")
        db.session.delete(asset)
        db.session.commit()

    return redirect(url_for('userassets.index', folder_id=asset.folder_id))


@bp.route('/edit/<uuid:fileid>/<string:filename>/move', methods=['POST', ])
@login_required
def move(fileid, filename):
    asset = Asset.query.get(fileid)
    redirect_id = asset.folder.id
    form = MoveAssetForm(prefix="moveasset")
    if form.validate_on_submit():
        if asset.owner != current_user.profile:
            abort(403)
        destinationfolder = form.folder.data
        logger.debug(f"Move {asset.system_path} to {destinationfolder.system_path}")
        os.replace(asset.system_path, os.path.join(destinationfolder.system_path, asset.filename))
        asset.folder = destinationfolder
        db.session.commit()
        flash("You moved your file")

    return redirect(url_for('userassets.index', folder_id=redirect_id))
