import json
import time

from flask import render_template, request, flash
from flask import redirect, url_for, jsonify
from flask_login import login_required, current_user

from werkzeug.exceptions import abort


from . import bp, api

from .models import Character
from .forms import ImportForm, CreateForm, SkillForm
from app import db


def get_character(id, check_author=True):
    character = Character.query.get(id)

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if check_author and character.user_id != current_user.id:
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

    rows = Character.query.all()

    characters = []

    for row in rows:
        characters.append({
            'id': row.id,
            'username': row.user_id,
            'title': row.title,
            'created': row.timestamp,
            'data': json.loads(row.body)
            })

    return render_template('character/index.html.jinja')


@bp.route('/create/<string:chartype>', methods=('GET', 'POST'))
@login_required
def create(chartype=None):
    form = CreateForm()
    if form.validate_on_submit():
        char_data = render_template('character/blank_character.json.jinja',
                                    title=form.title.data,
                                    timestamp=time.time())
        c = Character(title=form.title.data,
                      body=char_data,
                      user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('character.view', id=c.id))
    return render_template('character/create.html.jinja', form=form, type=type)


@bp.route('/import/<string:type>', methods=('GET', 'POST'))
@bp.route('/import', methods=('GET', 'POST'))
@login_required
def import_character(type=None):
    form = ImportForm()
    if form.validate_on_submit():
        c = Character(title=form.title.data,
                      body=form.body.data,
                      user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('character.view', id=c.id))
    return render_template('character/import.html.jinja', form=form, type=None)


"""
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    character = get_character(id)

    if request.method == 'POST':
        title = request.form['title']
        # body = request.form['body']
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            flash("Implement update character")
            return redirect(url_for('character.index'))

    return render_template('character/update.html.jinja', character=character)
"""


@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    character = get_character(id, check_author=True)

    if request.method == "POST":
        update = request.get_json()

        for setting in update:
            character.set_attribute(setting)

        character.store_data()
        db.session.commit()

    return "OK"


@bp.route('/<int:id>/', methods=('GET', 'POST'))
def view(id):
    character = get_character(id, check_author=False)

    editable = False

    if current_user.is_authenticated and current_user.id == character.user_id:
        editable = True

    skillform = SkillForm()
    if editable and skillform.validate_on_submit():
        skills = character.skills()
        for skill in skills:
            if skillform.name.data == skill['name']:
                flash("Skill already exists")
                return redirect(url_for('character.view', id=id))

        character.add_skill(skillform.name.data)
        character.store_data()
        db.session.commit()
        return redirect(url_for('character.view', id=id))

    return render_template('character/sheet.html.jinja',
                           character=character,
                           editable=editable,
                           skillform=skillform)


@api.route('/<int:id>/', methods=('GET', ))
def get(id):
    """API call to get all character data."""
    data = get_character(id)
    return jsonify(data.to_dict())


@bp.route('/<int:id>/delete', methods=('POST', ))
@api.route('/<int:id>/delete', methods=('POST', ))
def delete(id):
    """Delete a character."""
    get_character(id)
    flash("Implement deletion of character")
    return redirect(url_for('character.index'))


@bp.route('/<int:id>/export', methods=('GET', ))
def export(id):
    """Exports charcter data to JSON."""
    data = get_character(id)
    return jsonify(data.get_sheet())


@bp.route('/<int:id>/editjson', methods=('GET', 'POST'))
def editjson(id):
    """Lets the user edit the raw json of the character."""
    c = get_character(id)
    form = ImportForm()
    if form.validate_on_submit():
        c.title = form.title.data
        c.body = form.body.data
        db.session.commit()
        return redirect(url_for('character.view', id=c.id))

    form.body.data = c.body
    form.title.data = c.title
    form.submit.label.text = 'Save'

    return render_template('character/import.html.jinja', title="Edit JSON", form=form, type=None)
