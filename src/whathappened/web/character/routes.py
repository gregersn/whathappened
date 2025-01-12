import copy
import logging
from typing import Optional

from flask import render_template, request
from flask import redirect, url_for, jsonify
from werkzeug.exceptions import abort

from whathappened.web.auth.utils import login_required, current_user
from whathappened.web.content.forms import ChooseFolderForm
from whathappened.core.database import session
from whathappened.core.database.pagination import paginate
from whathappened.core.database.models import Invite, LogEntry
from whathappened.core.sheets.mechanics import core
from whathappened.core.sheets.mechanics.core import GameSystems
from whathappened.core.sheets.schema.base import CURRENT_SCHEMA_VERSION
from whathappened.core.sheets.schema.build import flatten_schema, get_schema, sub_schema
from whathappened.core.sheets.schema.utils import migrate

from .blueprints import bp, api
from ...core.character.models import Character
from .forms import EditForm, CreateForm, ImportForm
from .forms import DeleteForm

# Imports for registering games.
from . import coc7e  # noqa
from whathappened.core.sheets.mechanics.coc7e.convert import convert_from_dholes
from . import tftl  # noqa


logger = logging.getLogger(__name__)


def get_character(id: int, check_author: bool = True) -> Character:
    character = session.get(Character, id)

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if current_user.has_role("admin"):  # pyright: ignore[reportGeneralTypeIssues]
        return character

    if character.viewable_by(current_user.profile):
        return character

    if check_author and character.user_id != current_user.profile.id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(403)

    return character


@bp.route("/")
def index():
    return redirect("/")


@bp.route("/create/<string:chartype>/", methods=("GET", "POST"))
def create(chartype: str):
    character_module = globals()[chartype] if chartype in globals() else core

    form = getattr(character_module, "CreateForm", CreateForm)()
    template = getattr(
        character_module, "CREATE_TEMPLATE", "character/create.html.jinja"
    )

    if form.validate_on_submit():
        logger.debug(f"Creating new character specified by {form.data}")
        char_data = character_module.new_character(**form.data)
        assert isinstance(char_data, dict)
        c = Character(
            title=form.title.data, body=char_data, user_id=current_user.profile.id
        )  # pyright: ignore[reportGeneralTypeIssues]
        session.add(c)
        session.commit()
        return redirect(url_for("character.view", id=c.id))

    form.system.data = chartype
    return render_template(template, form=form, type=type)


@bp.route("/create/", methods=("GET",))
@login_required
def system_select(chartype=None):
    return render_template("character/system_select.html.jinja", systems=GameSystems)


@bp.route("/import/<string:type>", methods=("GET", "POST"))
@bp.route("/import/<int:id>", methods=("GET", "POST"))
@bp.route("/import/<uuid:code>", methods=("GET", "POST"))
@bp.route("/import", methods=("GET", "POST"))
@login_required
def import_character(
    type: Optional[str] = None, id: Optional[int] = None, code: Optional[str] = None
):
    logger.debug(f"{type}, {code}, {id}")
    character = None
    if id:
        character = get_character(id, check_author=True)
    elif code is not None:
        invite = session.get(Invite, code)
        if invite is None or invite.table != Character.__tablename__:
            return "Invalid code"
        character = session.get(Character, invite.object_id)

    form = ImportForm(obj=character)
    if form.validate_on_submit():
        c = Character(
            title=form.title.data, body=form.body.data, user_id=current_user.profile.id
        )  # pyright: ignore[reportGeneralTypeIssues]
        session.add(c)
        session.commit()
        return redirect(url_for("character.view", id=c.id))
    return render_template("character/import.html.jinja", form=form, type=None)


@bp.route("/<int:id>/update", methods=("POST",))
@login_required
def update(id: int):
    character = get_character(id, check_author=True)

    if request.method == "POST":
        update = request.get_json()
        assert update is not None
        for setting in update:
            name = character.set_attribute(setting)
            field = setting["field"]
            subfield = setting.get("subfield", "")
            value = setting["value"]
            type = setting.get("type", "value")
            if type == "portrait" and value is not None:
                value = "[image]"

            log_subfield = ""
            if subfield is not None and subfield != "None":
                log_subfield = " " + subfield
            if name is not None:
                log_message = f"set {type} on {field}{log_subfield} ({name}): {value}"
            else:
                log_message = f"set {type} on {field}{log_subfield}: {value}"

            logentry = LogEntry(character, log_message, user_id=current_user.id)  # pyright: ignore[reportGeneralTypeIssues]
            session.add(logentry)

        character.store_data()
        session.commit()

    return "OK"


def render_character(
    character: Character, editable: bool = False, code: Optional[str] = None
):
    if editable:
        if (not character.archived) and character.validate():
            logger.debug("Character sheet invalid, trying migration.")
            backup_data = copy.deepcopy(character.body)
            data = character.body
            try:
                prev_version = character.schema_version
                character.body = migrate(data, CURRENT_SCHEMA_VERSION)
                if not character.validate():
                    logentry = LogEntry(
                        character,
                        "Character was automatically migrated.",
                        user_id=current_user.id,
                    )  # pyright: ignore[reportGeneralTypeIssues]
                    session.add(logentry)

                    backup_character = Character(
                        title=f"{character.title}-{prev_version}-backup",
                        body=backup_data,
                        user_id=character.user_id,
                        archived=True,
                    )
                    session.add(backup_character)
                    session.commit()
            except KeyError:
                ...

        if character.system is None or character.validate():
            return redirect(url_for("character.edit", id=character.id))

    character_module = (
        globals()[character.system] if character.system in globals() else core
    )

    system_view = getattr(character_module, "view", None)

    if system_view is not None:
        return system_view(character.id, character, editable)

    system_template = getattr(character_module, "CHARACTER_SHEET_TEMPLATE", None)

    if system_template:
        return render_template(
            character_module.CHARACTER_SHEET_TEMPLATE,
            character=character,
            editable=editable,
            code=code,
        )

    return render_general_view(
        character.system, character=character, editable=editable, code=code
    )


@bp.route("/<uuid:code>", methods=("GET",))
def shared(code: str):
    invite = session.get(Invite, code)
    if invite is None or invite.table != Character.__tablename__:
        return "Invalid code"

    character = session.get(Character, invite.object_id)

    return render_character(character, editable=False, code=code)


@bp.route("/<int:id>/", methods=("GET", "POST"))
@login_required
def view(id: int):
    character = get_character(id, check_author=True)

    editable = current_user.is_authenticated and character.editable_by(
        current_user.profile
    )

    return render_character(character, editable=editable)


def html_data_type(t: str) -> str:
    if t == "integer":
        return "number"
    return t


def render_general_view(
    system: str, character: Character, editable: bool, code: Optional[str] = None
):
    logger.debug("Getting schema")
    schema = get_schema(system)
    schema = flatten_schema(schema)
    return render_template(
        "character/general_character.html.jinja",
        schema=schema,
        character=character,
        editable=editable,
        html_data_type=html_data_type,
        get_ref=sub_schema,
        code=code,
    )


@bp.route("/<int:id>/tokens/", methods=("GET", "POST"))
@login_required
def tokens(id: int):
    character = get_character(id, check_author=False)

    return render_template("character/tokens.html.jinja", picture=character.portrait)


@api.route("/<int:id>/", methods=("GET",))
def get(id: int):
    """API call to get all character data."""
    data = get_character(id, check_author=True)
    return jsonify(data.to_dict())


@bp.route(
    "/<int:id>/delete",
    methods=(
        "GET",
        "POST",
    ),
)
@api.route(
    "/<int:id>/delete",
    methods=(
        "GET",
        "POST",
    ),
)
@login_required
def delete(id: int):
    """Delete a character."""
    character = get_character(id, check_author=True)

    if current_user.profile.id != character.user_id:  # pyright: ignore[reportGeneralTypeIssues]
        abort(404)

    form = DeleteForm()
    if form.validate_on_submit():
        session.delete(character)
        session.commit()
        return redirect(url_for("character.index"))

    form.character_id.data = character.id

    return render_template(
        "character/delete_character.html.jinja", form=form, character=character
    )


@api.route("/<int:id>/share", methods=("GET",))
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

    share_url = url_for("character.shared", code=invite.id, _external=True)

    form = None

    html_response = render_template(
        "character/api_share.html.jinja", form=form, url=share_url, code=invite.id
    )

    return jsonify({"url": share_url, "html": html_response})


@bp.route("/<int:id>/export", methods=("GET",))
def export(id: int):
    """Exports charcter data to JSON."""
    data = get_character(id, check_author=True)
    return jsonify(data.get_sheet())


@bp.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id: int):
    """Lets the user edit the raw json of the character."""
    c = get_character(id, check_author=True)
    form = EditForm(obj=c)

    if form.validate_on_submit():
        assert form.body.data is not None
        assert form.title.data is not None
        c.title = form.title.data
        c.body = form.body.data
        c.archived = form.archived.data

        if form.migration.data:
            logger.debug("Trying to migrate data")
            data = form.body.data
            try:
                c.body = migrate(data, CURRENT_SCHEMA_VERSION)
            except KeyError:
                pass
        elif form.conversion.data:
            logger.debug("Conversion is checked")
            data = form.body.data
            c.body = convert_from_dholes(data)

        logentry = LogEntry(c, "JSON edited", user_id=current_user.id)  # pyright: ignore[reportGeneralTypeIssues]
        session.add(logentry)

        session.commit()
        return redirect(url_for("character.view", id=c.id))

    form.submit.label.text = "Save"

    validation_errors = c.validate()

    return render_template(
        "character/edit.html.jinja",
        title="Edit",
        validation_errors=validation_errors,
        form=form,
        character=c,
        type=None,
    )


@bp.route("/<int:character_id>/eventlog", methods=("GET",))
@login_required
def eventlog(character_id: int):
    page = request.args.get("page", 1, type=int)
    c = get_character(character_id, check_author=True)
    entries_page = paginate(LogEntry.query_for(c), page, 50)
    next_url = (
        url_for(
            "character.eventlog", character_id=character_id, page=entries_page.next_page
        )
        if entries_page.has_next
        else None
    )

    prev_url = (
        url_for(
            "character.eventlog", character_id=character_id, page=entries_page.prev_page
        )
        if entries_page.has_prev
        else None
    )
    logger.debug(next_url)
    log_entries = entries_page.items
    return render_template(
        "character/eventlog.html.jinja",
        character=c,
        entries=log_entries,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/<int:id>/folder", methods=("GET", "POST"))
@login_required
def folder(id: int):
    c = get_character(id, check_author=True)
    form = ChooseFolderForm()
    if form.validate_on_submit():
        c.folder = form.folder_id.data  # type: ignore
        session.commit()

    return render_template(
        "character/move_to_folder.html.jinja", form=form, character=c
    )
