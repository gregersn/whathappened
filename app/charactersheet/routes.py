import json
from functools import reduce

from jsoncomment import JsonComment

from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

from . import bp, api, get_character

from .models import Character
from app import db


@bp.route('/')
def index():
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


@bp.route('/create/<string:type>', methods=('GET', 'POST'))
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(type=None):
    if request.method == 'POST':
        title = request.form['title']
        body = request.form.get('body', "{}")
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            c = Character(title=title, body=body, user_id=current_user.id)
            db.session.add(c)
            db.session.commit()
            return redirect(url_for('character.view', id=c.id))

    return render_template('character/create.html.jinja', type=type)


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


@bp.route('/<int:id>/', methods=('GET', 'POST'))
def view(id):
    data = get_character(id, check_author=False)

    character_data = json.loads(data.body)

    if 'Investigator' not in character_data:
        blank = render_template('character/blank_character.json.jinja')
        character_data = JsonComment(json).loads(blank)

    if request.method == "POST":
        update = request.get_json()

        for setting in update:
            if setting.get('type', None) == 'skill':
                path, skill = setting['field'].split('#')
                subfield = setting.get('subfield', None)
                value = setting.get('value')
                skills = reduce(lambda x, y: x[y], path.split("."),
                                character_data['Investigator'])
                for s in skills:
                    if s['name'] == skill:
                        if (subfield is not None
                                and subfield != s.get('subskill', 'None')):
                            continue
                        s['value'] = value
                continue

            elif setting.get('type', None) == 'skillcheck':
                path, skill = setting['field'].split('#')
                subfield = setting.get('subfield', None)
                check = setting.get('value', False)
                skills = reduce(lambda x, y: x[y], path.split("."),
                                character_data['Investigator'])
                for s in skills:
                    if s['name'] == skill:
                        if (subfield is not None
                                and subfield != s.get('subskill', 'None')):
                            continue
                        s['checked'] = check
                continue
            else:
                s = reduce(lambda x, y: x[y], setting['field'].split(".")[:-1],
                           character_data['Investigator'])
                s[setting['field'].split(".")[-1]] = setting['value']

        data.body = json.dumps(character_data)
        db.session.commit()

    investigator = character_data['Investigator']
    # for skill in investigator['Skills']['Skill']:
    #     print(skill)
    character = {
        'id': id,
        'data': investigator
    }
    editable = False
    if current_user.is_authenticated and current_user.id == data.user_id:
        editable = True
    return render_template('character/sheet.html.jinja',
                           character=character,
                           editable=editable)


@api.route('/<int:id>/', methods=('GET', ))
def get(id):
    data = get_character(id)
    return jsonify(data.to_dict())


@bp.route('/<int:id>/delete', methods=('POST', ))
@api.route('/<int:id>/delete', methods=('POST', ))
def delete(id):
    get_character(id)
    flash("Implement deletion of character")
    return redirect(url_for('character.index'))
