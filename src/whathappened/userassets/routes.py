import os
from pathlib import Path
import logging

from typing import Optional
from flask import render_template, flash
from flask import redirect, url_for
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort

from whathappened.database import session
from whathappened.auth.utils import login_required, current_user

from .blueprints import bp
from .forms import DeleteAssetFolderForm, DeleteAssetForm
from .forms import UploadForm, NewFolderForm, MoveAssetForm
from .models import Asset, AssetFolder


logger = logging.getLogger(__name__)


@bp.route("/<uuid:folder_id>/")
@bp.route("/")
@login_required
def index(folder_id: Optional[str] = None):
    if current_user.profile.assetfolders.count() < 1:
        logger.debug("Creating initial folder")
        rootfolder = AssetFolder(title="assets", owner=current_user.profile)
        session.add(rootfolder)
        session.commit()

    if folder_id is not None:
        folder = session.get(AssetFolder, folder_id)
    else:
        folder = current_user.profile.assetfolders
        folder = folder.filter(AssetFolder.parent_id.__eq__(None)).first()

    assert folder

    form = UploadForm(folder_id=folder.id, prefix="fileupload")
    folderform = NewFolderForm(parent_id=folder.id, prefix="newfolderform")
    deletefolderform = DeleteAssetFolderForm(id=folder.id, prefix="deletefolderform")

    return render_template(
        "userassets/assets.html.jinja",
        form=form,
        folderform=folderform,
        deletefolderform=deletefolderform,
        folder=folder,
    )


@bp.route(
    "/folder/<uuid:folder_id>/",
    methods=[
        "POST",
    ],
)
@bp.route(
    "/folder/",
    methods=[
        "POST",
    ],
)
@login_required
def create_folder(folder_id=None):
    folderform = NewFolderForm(prefix="newfolderform")
    if folderform.validate_on_submit():
        logger.debug("Create a new folder")
        folder = AssetFolder(
            parent_id=folderform.parent_id.data,
            title=folderform.title.data,
            owner=current_user.profile,
        )
        session.add(folder)
        session.commit()
    return redirect(url_for("userassets.index", folder_id=folder_id))


@bp.route(
    "/folder/<uuid:id>/delete",
    methods=[
        "POST",
    ],
)
@login_required
def delete_folder(id):
    deletefolderform = DeleteAssetFolderForm(prefix="deletefolderform")
    folder = session.get(AssetFolder, id)
    assert folder
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
            logger.debug(
                f"Wrong ids specified {folder.id} " f"and {deletefolderform.id.data}"
            )
            abort(403)

        if folder.files:
            logger.debug("Folder contains files")
            abort(403)

        session.delete(folder)
        session.commit()
        return redirect(url_for("userassets.index", folder_id=parent_id))

    return redirect(url_for("userassets.index", folder_id=id))


@bp.route(
    "/<uuid:folder_id>/",
    methods=[
        "POST",
    ],
)
@bp.route(
    "/",
    methods=[
        "POST",
    ],
)
@login_required
def upload_file(folder_id=None):
    form = UploadForm(prefix="fileupload")
    if form.validate_on_submit():
        fileobject = form.uploaded.data
        folder: AssetFolder = session.get(AssetFolder, form.folder_id.data)
        assert folder
        if folder.owner != current_user.profile:
            abort(403)

        if fileobject.filename:
            filename = secure_filename(fileobject.filename)

            folder.system_path.mkdir(parents=True, exist_ok=True)
            fileobject.save(folder.system_path / filename)

            asset = Asset(
                filename=fileobject.filename, folder=folder, owner=current_user.profile
            )
            session.add(asset)
            session.commit()

    return redirect(url_for("userassets.index", folder_id=folder_id))


@bp.route("/view/<uuid:fileid>/<string:filename>")
@login_required
def view(fileid, filename):
    """Retrieve a user asset."""
    userasset: Asset = session.get(Asset, fileid)
    assert userasset
    if filename != userasset.filename:
        abort(404)

    filepath = userasset.folder.get_path()
    assetname = secure_filename(str(userasset.filename))
    logger.debug("Sending file from %s, %s", filepath, assetname)

    full_dir = Path(userasset.folder.system_path)
    logger.debug("%s/%s", full_dir.absolute(), assetname)
    return send_from_directory(str(full_dir.absolute()), assetname)


@bp.route("/edit/<uuid:fileid>/<string:filename>")
@login_required
def edit(fileid, filename):
    userasset = session.get(Asset, fileid)
    assert userasset
    if filename != userasset.filename:
        abort(404)

    deleteform = DeleteAssetForm(id=userasset.id, prefix="deleteasset")
    moveform = MoveAssetForm(
        id=userasset.id, prefix="moveasset", folder=userasset.folder
    )

    return render_template(
        "userassets/edit.html.jinja",
        asset=userasset,
        deleteform=deleteform,
        moveform=moveform,
    )


@bp.route(
    "/edit/<uuid:fileid>/<string:filename>/delete",
    methods=[
        "POST",
    ],
)
@login_required
def delete(fileid, filename):
    logger.debug("Delete asset")
    asset = session.get(Asset, fileid)
    assert asset
    form = DeleteAssetForm(prefix="deleteasset")
    if form.validate_on_submit():
        if asset.owner != current_user.profile:
            abort(403)
        flash("You just deleted an asset")
        session.delete(asset)
        session.commit()

    return redirect(url_for("userassets.index", folder_id=asset.folder_id))


@bp.route(
    "/edit/<uuid:fileid>/<string:filename>/move",
    methods=[
        "POST",
    ],
)
@login_required
def move(fileid, filename):
    asset = session.get(Asset, fileid)
    assert asset
    redirect_id = asset.folder.id
    form = MoveAssetForm(prefix="moveasset")
    if form.validate_on_submit():
        if asset.owner != current_user.profile:
            abort(403)
        destinationfolder = form.folder.data
        full_src_folder = asset.folder.system_path
        full_dst_folder = destinationfolder.system_path
        logger.debug(full_src_folder)
        logger.debug(full_dst_folder)
        if destinationfolder is not None:
            logger.debug(
                "Move %s to %s", asset.system_path, destinationfolder.system_path
            )
            if not full_dst_folder.is_dir():
                full_dst_folder.mkdir(parents=True)
            os.replace(
                full_src_folder / asset.filename, full_dst_folder / asset.filename
            )
            asset.folder = destinationfolder
            session.commit()
            flash("You moved your file")

    return redirect(url_for("userassets.index", folder_id=redirect_id))
