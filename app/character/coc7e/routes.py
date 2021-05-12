from flask import redirect, render_template, url_for, flash
from flask_login import current_user

from ..forms import SkillForm, SubskillForm
from app.models import LogEntry, Invite
from app.database import session
from . import utils  # noqa # import to register filters


def view(id, character, editable):
    subskillform = SubskillForm(prefix="subskillform")
    if editable and subskillform.data and subskillform.validate_on_submit():
        character.add_subskill(subskillform.name.data,
                               subskillform.parent.data)
        logentry = LogEntry(character,
                            f"add subskill {subskillform.name.data} " +
                            f"under {subskillform.parent.data}",
                            user_id=current_user.id)
        session.add(logentry)

        character.store_data()
        session.commit()
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
        logentry = LogEntry(
            character,
            f"add skill {subskillform.name.data}",
            user_id=current_user.id)
        session.add(logentry)

        session.commit()
        return redirect(url_for('character.view', id=id))

    typeheader = "1920s Era Investigator"
    if character.game and character.game[1] == "Modern":
        typeheader = "Modern Era"

    shared = Invite.query_for(character).count()

    return render_template('character/coc7e/sheet.html.jinja',
                           shared=shared,
                           character=character,
                           typeheader=typeheader,
                           editable=editable,
                           skillform=skillform,
                           subskillform=subskillform)
