"""Routes for character interaction."""

import logging
from typing import Optional

from flask import render_template, request
from flask import redirect, url_for, jsonify
from werkzeug.exceptions import abort

from whathappened.core.database import session
from whathappened.core.database.models import Invite, LogEntry
from whathappened.core.database.pagination import paginate
from whathappened.core.sheets.mechanics import core
from whathappened.core.sheets.mechanics.core import GameSystems
from whathappened.core.sheets.schema.base import CURRENT_SCHEMA_VERSION
from whathappened.core.sheets.schema.utils import migrate
from whathappened.web.auth.utils import login_required, current_user
from whathappened.web.character.views import get_character, render_character
from whathappened.web.content.forms import ChooseFolderForm
from whathappened.core.sheets.mechanics.coc7e.convert import convert_from_dholes

from .blueprints import bp, api
from ...core.character.models import Character
from .forms import EditForm, CreateForm, ImportForm
from .forms import DeleteForm

# Imports for registering games.
from . import coc7e  # noqa: F401 # pylint: disable=W0611
from . import tftl  # noqa: F401 # pylint: disable=W0611


logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """Currently no index view for characters."""
    return redirect("/")


@bp.route("/create/<string:character_type>/", methods=("GET", "POST"))
def create(character_type: str):
    """Create character route."""
    character_module = (
        globals()[character_type] if character_type in globals() else core
    )

    form = getattr(character_module, "CreateForm", CreateForm)()
    template = getattr(
        character_module, "CREATE_TEMPLATE", "character/create.html.jinja"
    )

    if form.validate_on_submit():
        logger.debug("Creating new character specified by %s", form.data)
        char_data = character_module.new_character(**form.data)
        assert isinstance(char_data, dict)
        c = Character(
            title=form.title.data, body=char_data, user_id=current_user.profile.id
        )
        session.add(c)
        session.commit()
        return redirect(url_for("character.view", id=c.id))

    form.system.data = character_type
    return render_template(template, form=form, type=type)


@bp.route("/create/", methods=("GET",))
@login_required
def system_select():
    """Show system select view."""
    return render_template("character/system_select.html.jinja", systems=GameSystems)


@bp.route("/import/<string:character_type>", methods=("GET", "POST"))
@bp.route("/import/<int:character_id>", methods=("GET", "POST"))
@bp.route("/import/<uuid:code>", methods=("GET", "POST"))
@bp.route("/import", methods=("GET", "POST"))
@login_required
def import_character(
    character_type: Optional[str] = None,
    character_id: Optional[int] = None,
    code: Optional[str] = None,
):
    """Import character from other system."""
    logger.debug("%s, %s, %s", character_type, code, character_id)
    character = None
    if character_id:
        character = get_character(character_id, check_owner=True)
    elif code is not None:
        invite = session.get(Invite, code)
        if invite is None or invite.table != Character.__tablename__:
            return "Invalid code"
        character = session.get(Character, invite.object_id)

    form = ImportForm(obj=character)
    if form.validate_on_submit():
        c = Character(
            title=form.title.data, body=form.body.data, user_id=current_user.profile.id
        )
        session.add(c)
        session.commit()
        return redirect(url_for("character.view", id=c.id))
    return render_template("character/import.html.jinja", form=form, type=None)


@bp.route("/<int:character_id>/update", methods=("POST",))
@login_required
def update(character_id: int):
    """Update character data."""
    character = get_character(character_id, check_owner=True)

    if request.method == "POST":
        updated_data = request.get_json()
        assert updated_data is not None
        for setting in updated_data:
            name = character.set_attribute(setting)
            field = setting["field"]
            subfield = setting.get("subfield", "")
            value = setting["value"]
            data_type = setting.get("type", "value")
            if data_type == "portrait" and value is not None:
                value = "[image]"

            log_subfield = ""
            if subfield is not None and subfield != "None":
                log_subfield = " " + subfield
            if name is not None:
                log_message = (
                    f"set {data_type} on {field}{log_subfield} ({name}): {value}"
                )
            else:
                log_message = f"set {data_type} on {field}{log_subfield}: {value}"

            logentry = LogEntry(character, log_message, user_id=current_user.id)
            session.add(logentry)

        character.store_data()
        session.commit()

    return "OK"


@bp.route("/<uuid:code>", methods=("GET",))
def shared(code: str):
    """View a character based on a sharing  code."""
    invite = session.get(Invite, code)
    if invite is None or invite.table != Character.__tablename__:
        return "Invalid code"

    character = session.get(Character, invite.object_id)

    return render_character(character, editable=False, code=code)


@bp.route("/<int:character_id>/", methods=("GET", "POST"))
@login_required
def view(character_id: int):
    """View a character."""
    character = get_character(character_id, check_owner=True)

    editable = current_user.is_authenticated and character.editable_by(
        current_user.profile
    )

    return render_character(character, editable=editable)


@bp.route("/<int:character_id>/tokens/", methods=("GET", "POST"))
@login_required
def tokens(character_id: int):
    """Show tokens created from character picture."""
    character = get_character(character_id, check_owner=False)

    return render_template("character/tokens.html.jinja", picture=character.portrait)


@api.route("/<int:character_id>/", methods=("GET",))
def get(character_id: int):
    """API call to get all character data."""
    data = get_character(character_id, check_owner=True)
    return jsonify(data.to_dict())


@bp.route(
    "/<int:character_id>/delete",
    methods=(
        "GET",
        "POST",
    ),
)
@api.route(
    "/<int:character_id>/delete",
    methods=(
        "GET",
        "POST",
    ),
)
@login_required
def delete(character_id: int):
    """Delete a character."""
    character = get_character(character_id, check_owner=True)

    if current_user.profile.id != character.user_id:
        abort(404)

    form = DeleteForm()
    if form.validate_on_submit():
        session.delete(character)
        session.commit()
        return redirect(url_for("character.index"))

    form.character_id.data = str(character.id)

    return render_template(
        "character/delete_character.html.jinja", form=form, character=character
    )


@api.route("/<int:character_id>/share", methods=("GET",))
@login_required
def share(character_id: int):
    """Share a character."""
    character = get_character(character_id, check_owner=True)
    logger.debug("Finding previous invite")
    invite = Invite.query_for(character).first()
    logger.debug("Invites found: %s", invite)

    if not invite:
        logger.debug("Creating an invite for character %s", character.id)
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


@bp.route("/<int:character_id>/export", methods=("GET",))
def export(character_id: int):
    """Exports charcter data to JSON."""
    data = get_character(character_id, check_owner=True)
    return jsonify(data.get_sheet())


@bp.route("/<int:character_id>/edit", methods=("GET", "POST"))
def edit(character_id: int):
    """Lets the user edit the raw json of the character."""
    c = get_character(character_id, check_owner=True)
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

        logentry = LogEntry(c, "JSON edited", user_id=current_user.id)
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
    """Show eventlog for character."""
    page = request.args.get("page", 1, type=int)
    c = get_character(character_id, check_owner=True)
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


@bp.route("/<int:character_id>/folder", methods=("GET", "POST"))
@login_required
def folder(character_id: int):
    """Move character to folder."""
    c = get_character(character_id, check_owner=True)
    form = ChooseFolderForm()
    if form.validate_on_submit():
        c.folder = form.folder_id.data  # type: ignore
        session.commit()

    return render_template(
        "character/move_to_folder.html.jinja", form=form, character=c
    )
