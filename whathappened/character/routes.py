import os
from pathlib import Path
from whathappened.character import core
from whathappened.character.core import CHARACTER_SCHEMA_DIR, GameSystems
from whathappened.character.schema import load_schema, sub_schema
import logging

from flask import render_template, request
from flask import redirect, url_for, jsonify
from flask_login import login_required, current_user

from werkzeug.exceptions import abort


from . import bp, api

from .models import Character
from .forms import ImportForm, CreateForm
from .forms import DeleteForm

# Imports for registering games.
from . import coc7e
from . import tftl  # noqa

from whathappened.models import LogEntry
from whathappened.utils.schema import migrate
from whathappened.models import Invite
from whathappened.character.schema.coc7e import migrations, latest
from whathappened.database import session, paginate

from whathappened.content.forms import ChooseFolderForm

logger = logging.getLogger(__name__)


def get_character(id: int, check_author: bool = True) -> Character:
    character = Character.query.get(id)

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if current_user.has_role('admin'):
        return character

    if character.campaigns:
        logger.debug("Checking if character is in same campaign as user")
        for campaign in character.campaigns:
            if current_user.profile in campaign.players \
                    or campaign in current_user.profile.campaigns:
                logger.debug(f"Character '{character.title}' " +
                             f"is in '{campaign.title}' " +
                             f"with '{current_user.username}''")
                return character

    if check_author and character.user_id != current_user.profile.id:
        abort(403)

    return character


@bp.route('/')
def index():
    return redirect("/")


@bp.route('/create/<string:chartype>/', methods=('GET', 'POST'))
def create(chartype: str):

    character_module = globals()[chartype] if chartype in globals() else core

    form = getattr(character_module, 'CreateForm', CreateForm)()
    template = getattr(character_module, 'CREATE_TEMPLATE',
                       'character/create.html.jinja')

    if form.validate_on_submit():
        logger.debug(f"Creating new character specified by {form.data}")
        char_data = character_module.new_character(**form.data)
        c = Character(title=form.title.data,
                      body=char_data,
                      user_id=current_user.profile.id)
        session.add(c)
        session.commit()
        return redirect(url_for('character.view', id=c.id))

    form.system.data = chartype
    return render_template(template, form=form, type=type)


@bp.route('/create/', methods=('GET', ))
@login_required
def system_select(chartype=None):
    return render_template('character/system_select.html.jinja',
                           systems=GameSystems)


@bp.route('/import/<string:type>', methods=('GET', 'POST'))
@bp.route('/import/<int:id>', methods=('GET', 'POST'))
@bp.route('/import/<uuid:code>', methods=('GET', 'POST'))
@bp.route('/import', methods=('GET', 'POST'))
@login_required
def import_character(type=None, id: int = None, code: str = None):
    logger.debug(f"{type}, {code}, {id}")
    character = None
    if id:
        character = get_character(id, check_author=True)
    elif code is not None:
        invite = Invite.query.get(code)
        if invite is None or invite.table != Character.__tablename__:
            return "Invalid code"
        character = Character.query.get(invite.object_id)

    form = ImportForm(obj=character)
    if form.validate_on_submit():
        c = Character(title=form.title.data,
                      body=form.body.data,
                      user_id=current_user.profile.id)
        session.add(c)
        session.commit()
        return redirect(url_for('character.view', id=c.id))
    return render_template('character/import.html.jinja', form=form, type=None)


@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id: int):
    character = get_character(id, check_author=True)

    if request.method == "POST":
        update = request.get_json()

        for setting in update:
            character.set_attribute(setting)
            field = setting['field']
            subfield = setting.get('subfield', '')
            value = setting['value']
            type = setting.get('type', 'value')
            if type == 'portrait' and value is not None:
                value = "[image]"

            log_subfield = ''
            if subfield is not None and subfield != 'None':
                log_subfield = ' ' + subfield
            log_message = (f"set {type} on {field}{log_subfield}: {value}")

            logentry = LogEntry(character,
                                log_message,
                                user_id=current_user.id)
            session.add(logentry)

        character.store_data()
        session.commit()

    return "OK"


@bp.route('/<uuid:code>', methods=('GET', ))
def shared(code: str):
    invite = Invite.query.get(code)
    if invite is None or invite.table != Character.__tablename__:
        return "Invalid code"

    character = Character.query.get(invite.object_id)
    editable = False

    typeheader = "1920s Era Investigator"
    if character.game[1] == "Modern":
        typeheader = "Modern Era"

    return render_template('character/coc7e/sheet.html.jinja',
                           code=code,
                           character=character,
                           typeheader=typeheader,
                           editable=editable,
                           skillform=None,
                           subskillform=None)


@bp.route('/<int:id>/', methods=('GET', 'POST'))
@login_required
def view(id: int):
    character = get_character(id, check_author=True)

    editable = False

    if (current_user.is_authenticated and
            current_user.profile.id == character.user_id):
        editable = True

    for campaign in character.campaigns:
        if campaign.user_id == current_user.profile.id:
            editable = True
            break

    if (character.system is None or character.validate()) and editable:
        return redirect(url_for('character.editjson', id=id))

    character_module = (globals()[character.system]
                        if character.system in globals()
                        else core)

    system_view = getattr(character_module, 'view', None)

    if system_view is not None:
        return system_view(id, character, editable)

    system_template = getattr(
        character_module, 'CHARACTER_SHEET_TEMPLATE', None)

    if system_template:
        return render_template(character_module.CHARACTER_SHEET_TEMPLATE,
                               character=character,
                               editable=editable)

    character_schema = getattr(
        character_module, 'CHARACTER_SCHEMA', None)

    if character_schema is None:
        character_schema = CHARACTER_SCHEMA_DIR / f"{character.system}.yaml"

    return render_general_view(character_schema,
                               character=character,
                               editable=editable)


def html_data_type(t: str) -> str:
    if t == 'integer':
        return 'number'
    return t


def render_general_view(schema_file: Path,
                        character: Character,
                        editable: bool):
    schema = load_schema(schema_file)
    return render_template('character/general_character.html.jinja',
                           schema=schema,
                           character=character,
                           editable=editable,
                           html_data_type=html_data_type,
                           get_ref=sub_schema)


@bp.route('/<int:id>/tokens/', methods=('GET', 'POST'))
@login_required
def tokens(id: int):
    character = get_character(id, check_author=False)

    return render_template('character/tokens.html.jinja',
                           picture=character.portrait)


@api.route('/<int:id>/', methods=('GET', ))
def get(id: int):
    """API call to get all character data."""
    data = get_character(id, check_author=True)
    return jsonify(data.to_dict())


@bp.route('/<int:id>/delete', methods=('GET', 'POST', ))
@api.route('/<int:id>/delete', methods=('GET', 'POST', ))
@login_required
def delete(id: int):
    """Delete a character."""
    character = get_character(id, check_author=True)

    if current_user.profile.id != character.user_id:
        abort(404)

    form = DeleteForm()
    if form.validate_on_submit():
        session.delete(character)
        session.commit()
        return redirect(url_for('character.index'))

    form.character_id.data = character.id

    return render_template('character/delete_character.html.jinja',
                           form=form,
                           character=character)


@api.route('/<int:id>/share', methods=('GET', ))
@login_required
def share(id: int):
    """Share a character."""
    character = get_character(id, check_author=True)
    logger.debug("Finding previous invite")
    invite = Invite.query_for(character).first()
    logger.debug(f"Invites found {invite}")
    if not invite:
        logger.debug(f"Creating an invite for character {character.id}")
        invite = Invite(character)
        invite.owner_id = character.user_id
        session.add(invite)
        session.commit()

    share_url = url_for('character.shared', code=invite.id, _external=True)

    form = None

    html_response = render_template('character/api_share.html.jinja',
                                    form=form,
                                    url=share_url,
                                    code=invite.id)

    return jsonify({'url': share_url,
                    'html': html_response})


@bp.route('/<int:id>/export', methods=('GET', ))
def export(id: int):
    """Exports charcter data to JSON."""
    data = get_character(id, check_author=True)
    return jsonify(data.get_sheet())


@bp.route('/<int:id>/editjson', methods=('GET', 'POST'))
def editjson(id: int):
    """Lets the user edit the raw json of the character."""
    c = get_character(id, check_author=True)
    form = ImportForm(obj=c)

    if form.validate_on_submit():
        c.title = form.title.data
        c.body = form.body.data

        if form.migration.data:
            logger.debug("Trying to migrate data")
            data = form.body.data
            c.body = migrate(data,
                             latest,
                             migrations=migrations)
        elif form.conversion.data:
            logger.debug("Conversion is checked")
            data = form.body.data
            c.body = coc7e.convert_from_dholes(data)

        logentry = LogEntry(c, "JSON edited", user_id=current_user.id)
        session.add(logentry)

        session.commit()
        return redirect(url_for('character.view', id=c.id))

    form.submit.label.text = 'Save'

    validation_errors = c.validate()

    return render_template('character/import.html.jinja',
                           title="Edit JSON",
                           validation_errors=validation_errors,
                           form=form,
                           type=None)


@bp.route('/<int:id>/eventlog', methods=('GET', ))
@login_required
def eventlog(id: int):
    page = request.args.get('page', 1, type=int)
    c = get_character(id, check_author=True)
    entries_page = paginate(LogEntry.query_for(c), page, 50)
    """
    # TODO
    next_url = url_for('character.eventlog', id=id,
                       page=entries_page.next_num) \
        if entries_page.has_next else None

    prev_url = url_for('character.eventlog', id=id,
                       page=entries_page.prev_num) \
        if entries_page.has_prev else None
    """
    next_url = None
    prev_url = None
    logger.debug(next_url)
    log_entries = entries_page.items
    return render_template('character/eventlog.html.jinja',
                           character=c,
                           entries=log_entries,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/<int:id>/folder', methods=('GET', 'POST'))
@login_required
def folder(id: int):
    c = get_character(id, check_author=True)
    form = ChooseFolderForm()
    if form.validate_on_submit():
        c.folder = form.folder_id.data  # type: ignore
        session.commit()

    return render_template('character/move_to_folder.html.jinja',
                           form=form,
                           character=c)
