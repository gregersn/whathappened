from flask import render_template, redirect

from whathappened.database import session

from whathappened.character.models import Character
from whathappened.campaign import models as campaignmodels
from whathappened.auth import login_required, current_user

from . import bp

from .forms import NewFolderForm
from .models import Folder


@bp.route('/<uuid:folder_id>/', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def folders(folder_id=None):
    new_folder_form = NewFolderForm(prefix='new_folder')

    if new_folder_form.validate_on_submit():
        print("From validated, add folder")
        folder = Folder()
        new_folder_form.populate_obj(folder)
        session.add(folder)
        session.commit()
        return redirect('/content')
    else:
        print("Form did not validate")
        # return redirect(request.url)

    new_folder_form.owner_id.data = current_user.profile.id  # pyright: ignore[reportGeneralTypeIssues]
    new_folder_form.parent_id.data = folder_id

    current_folder = session.get(Folder, folder_id)

    folders = None
    characters = None
    campaigns = None
    tree = []

    if current_folder is None:
        folders = current_user.profile.folders.filter(  # pyright: ignore[reportGeneralTypeIssues]
            Folder.parent_id.__eq__(None))
        characters = current_user.profile.characters.filter(  # pyright: ignore[reportGeneralTypeIssues]
            Character.folder_id.__eq__(None))
        campaigns = current_user.profile.campaigns.filter(  # pyright: ignore[reportGeneralTypeIssues]
            campaignmodels.Campaign.folder_id.__eq__(None))

    else:
        folders = current_folder.subfolders
        characters = current_folder.characters
        campaigns = current_folder.campaigns
        f = current_folder
        while f.parent:
            tree.append(f.parent)
            f = f.parent
            tree.reverse()

    data = {
        'current_folder': current_folder,
        'tree': tree,
        'folders': folders,
        'characters': characters,
        'campaigns': campaigns
    }
    return render_template('content/folders.html.jinja', new_folder_form=new_folder_form, data=data)
