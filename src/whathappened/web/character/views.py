"""Character route functions."""

import copy

import logging
from typing import Optional, cast

from flask import render_template, redirect, url_for
from werkzeug.exceptions import abort


from whathappened.core.database import session
from whathappened.core.database.models import LogEntry
from whathappened.core.sheets.mechanics import core
from whathappened.core.sheets.schema.base import CURRENT_SCHEMA_VERSION, Gametag
from whathappened.core.sheets.schema.build import flatten_schema, get_schema, sub_schema
from whathappened.core.sheets.schema.utils import migrate
from whathappened.web.auth.utils import current_user

from ...core.character.models import Character

# Imports for registering games.
from . import coc7e  # noqa: F401 # pylint: disable=W0611
from . import tftl  # noqa: F401 # pylint: disable=W0611


logger = logging.getLogger(__name__)


def get_character(character_id: int, check_owner: bool = True) -> Character:
    """Get a character by id."""
    character = session.get(Character, character_id)

    if character is None:
        abort(404, f"Character id {character_id} doesn't exist.")

    if current_user.has_role("admin"):
        return character

    if character.viewable_by(current_user.profile):
        return character

    if check_owner and character.user_id != current_user.profile.id:
        abort(403)

    return character


def render_character(
    character: Character, editable: bool = False, code: Optional[str] = None
):
    """Render a character view."""
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
                    )
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
            return redirect(url_for("character.edit", character_id=character.id))

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
        cast(Gametag, character.system),
        character=character,
        editable=editable,
        code=code,
    )


def html_data_type(t: str) -> str:
    """Convert type names to html type names."""
    if t == "integer":
        return "number"
    return t


def render_general_view(
    system: Gametag, character: Character, editable: bool, code: Optional[str] = None
):
    """Render a general character view."""
    logger.debug("Getting schema for: %s", system)
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
