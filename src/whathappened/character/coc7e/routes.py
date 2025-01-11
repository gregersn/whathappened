from flask import redirect, render_template, url_for, flash

from whathappened.core.database.models import LogEntry, Invite
from whathappened.core.database import session
from whathappened.auth.utils import current_user

from ..forms import SkillForm, SubskillForm


def view(id, character, editable):
    subskillform = SubskillForm(prefix="subskillform")
    if editable and subskillform.data and subskillform.validate_on_submit():
        character.mechanics.add_subskill(
            subskillform.name.data, subskillform.parent.data
        )
        logentry = LogEntry(
            character,
            f"add subskill {subskillform.name.data} "
            + f"under {subskillform.parent.data}",
            user_id=current_user.id,
        )  # pyright: ignore[reportGeneralTypeIssues]
        session.add(logentry)

        character.store_data()
        session.commit()
        return redirect(url_for("character.view", id=id))

    skillform = SkillForm(prefix="skillform")
    if editable and skillform.data and skillform.validate_on_submit():
        skills = character.skills()
        for skill in skills:
            if skillform.name.data == skill["name"]:
                flash("Skill already exists")
                return redirect(url_for("character.view", id=id))

        character.add_skill(skillform.name.data)
        character.store_data()
        logentry = LogEntry(
            character, f"add skill {subskillform.name.data}", user_id=current_user.id
        )  # pyright: ignore[reportGeneralTypeIssues]
        session.add(logentry)

        session.commit()
        return redirect(url_for("character.view", id=id))

    shared = Invite.query_for(character).count()

    return render_template(
        "character/coc7e/sheet.html.jinja",
        shared=shared,
        character=character,
        editable=editable,
        skillform=skillform,
        subskillform=subskillform,
    )
