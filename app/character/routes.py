import json
import time
import logging

from flask import render_template, request, flash
from flask import redirect, url_for, jsonify
from flask_login import login_required, current_user

from werkzeug.exceptions import abort


from . import bp, api

from .models import Character
from .forms import ImportForm, CreateForm, SkillForm
from .forms import SubskillForm, DeleteForm
from .coc import convert_from_dholes
from app import db
from app.models import LogEntry
from app.utils.schema import migrate
from app.models import Invite
from app.character.schema.coc import migrations

logger = logging.getLogger(__name__)


def get_character(id, check_author=True):
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


@bp.app_template_filter('half')
def half(value):
    try:
        o = int(value, 10) // 2
        return o
    except Exception:
        return ''


@bp.app_template_filter('fifth')
def fifth(value):
    try:
        o = int(value, 10) // 5
        return o
    except Exception:
        return ''


@bp.route('/')
def index():
    return redirect("/")


@bp.route('/create/<string:chartype>', methods=('GET', 'POST'))
@login_required
def create(chartype=None):
    form = CreateForm()
    if form.validate_on_submit():
        char_data = render_template('character/blank_character.json.jinja',
                                    title=form.title.data,
                                    type=form.gametype.data,
                                    timestamp=time.time())
        c = Character(title=form.title.data,
                      body=json.loads(char_data),
                      user_id=current_user.profile.id)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('character.view', id=c.id))
    return render_template('character/create.html.jinja', form=form, type=type)


@bp.route('/import/<string:type>', methods=('GET', 'POST'))
@bp.route('/import/<int:id>', methods=('GET', 'POST'))
@bp.route('/import/<uuid:code>', methods=('GET', 'POST'))
@bp.route('/import', methods=('GET', 'POST'))
@login_required
def import_character(type=None, id=None, code=None):
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
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('character.view', id=c.id))
    return render_template('character/import.html.jinja', form=form, type=None)


@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    character = get_character(id, check_author=True)

    if request.method == "POST":
        update = request.get_json()

        for setting in update:
            character.set_attribute(setting)
            field = setting['field']
            subfield = setting.get('subfield', '')
            value = setting['value']
            type = setting.get('type', 'value')
            log_message = f"set {type} on {field}{' ' + subfield if subfield is not None and subfield != 'None' else '' }: {value}"
            logentry = LogEntry(character, log_message, user_id=current_user.id)
            db.session.add(logentry)

        character.store_data()
        db.session.commit()

    return "OK"


@bp.route('/<uuid:code>', methods=('GET', ))
def shared(code):
    invite = Invite.query.get(code)
    if invite is None or invite.table != Character.__tablename__:
        return "Invalid code"

    character = Character.query.get(invite.object_id)
    editable = False

    typeheader = "1920s Era Investigator"
    if character.game[1] == "Modern":
        typeheader = "Modern Era"

    return render_template('character/sheet.html.jinja',
                           code=code,
                           character=character,
                           typeheader=typeheader,
                           editable=editable,
                           skillform=None,
                           subskillform=None)


@bp.route('/<int:id>/', methods=('GET', 'POST'))
@login_required
def view(id):
    character = get_character(id, check_author=True)

    editable = False

    if (current_user.is_authenticated and
            current_user.profile.id == character.user_id):
        editable = True

    for campaign in character.campaigns:
        if campaign.user_id == current_user.profile.id:
            editable = True
            break

    subskillform = SubskillForm(prefix="subskillform")
    if editable and subskillform.data and subskillform.validate_on_submit():
        character.add_subskill(subskillform.name.data,
                               subskillform.parent.data)
        logentry = LogEntry(character, f"add subskill {subskillform.name.data} under {subskillform.parent.data}", user_id=current_user.id)
        db.session.add(logentry)

        character.store_data()
        db.session.commit()
        return redirect(url_for('character.view', id=id))

    skillform = SkillForm(prefix="skillform")
    if editable and skillform.data and skillform.validate_on_submit():
        skills = character.skills()
        for skill in skills:
            if skillform.name.data == skill['name']:
                flash("Skill already exists")
                return redirect(url_for('character.view', id=id))

        character.add_skill(skillform.name.data)
        character.store_data()
        logentry = LogEntry(character, f"add skill {subskillform.name.data}", user_id=current_user.id)
        db.session.add(logentry)

        db.session.commit()
        return redirect(url_for('character.view', id=id))

    typeheader = "1920s Era Investigator"
    if character.game and character.game[1] == "Modern":
        typeheader = "Modern Era"

    shared = Invite.query_for(character).count()

    if (character.game is None or character.validate()) and editable:
        return redirect(url_for('character.editjson', id=id))

    return render_template('character/sheet.html.jinja',
                           shared=shared,
                           character=character,
                           typeheader=typeheader,
                           editable=editable,
                           skillform=skillform,
                           subskillform=subskillform)


@api.route('/<int:id>/', methods=('GET', ))
def get(id):
    """API call to get all character data."""
    data = get_character(id, check_author=True)
    return jsonify(data.to_dict())


@bp.route('/<int:id>/delete', methods=('GET', 'POST', ))
@api.route('/<int:id>/delete', methods=('GET', 'POST', ))
@login_required
def delete(id):
    """Delete a character."""
    character = get_character(id, check_author=True)

    if current_user.profile.id != character.user_id:
        abort(404)

    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(character)
        db.session.commit()
        return redirect(url_for('character.index'))

    form.character_id.data = character.id

    return render_template('character/delete_character.html.jinja',
                           form=form,
                           character=character)


@api.route('/<int:id>/share', methods=('GET', ))
@login_required
def share(id):
    """Share a character."""
    character = get_character(id, check_author=True)
    logger.debug("Finding previous invite")
    invite = Invite.query_for(character).first()
    logger.debug(f"Invites found {invite}")
    if not invite:
        logger.debug(f"Creating an invite for character {character.id}")
        invite = Invite(character)
        invite.owner_id = character.user_id
        db.session.add(invite)
        db.session.commit()

    share_url = url_for('character.shared', code=invite.id, _external=True)

    form = None

    html_response = render_template('character/api_share.html.jinja',
                                    form=form,
                                    url=share_url,
                                    code=invite.id)

    return jsonify({'url': share_url,
                    'html': html_response})


@bp.route('/<int:id>/export', methods=('GET', ))
def export(id):
    """Exports charcter data to JSON."""
    data = get_character(id, check_author=True)
    return jsonify(data.get_sheet())


@bp.route('/<int:id>/editjson', methods=('GET', 'POST'))
def editjson(id):
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
                             "0.0.2",
                             migrations=migrations)
        elif form.conversion.data:
            logger.debug("Conversion is checked")
            data = form.body.data
            c.body = convert_from_dholes(data)

        logentry = LogEntry(c, f"JSON edited", user_id=current_user.id)
        db.session.add(logentry)

        db.session.commit()
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
    entries_page = LogEntry.query_for(c).paginate(page, 50, False)
    next_url = url_for('character.eventlog', id=id,
                       page=entries_page.next_num) \
        if entries_page.has_next else None

    prev_url = url_for('character.eventlog', id=id,
                       page=entries_page.prev_num) \
        if entries_page.has_prev else None

    logger.debug(next_url)
    log_entries = entries_page.items
    return render_template('character/eventlog.html.jinja',
                           character=c,
                           entries=log_entries,
                           next_url=next_url,
                           prev_url=prev_url)
