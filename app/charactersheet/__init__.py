import json
from functools import reduce
from jsoncomment import JsonComment
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)

from flask_login import login_required, current_user
from flask_assets import Bundle
from werkzeug.exceptions import abort

from app import db, assets
from flask import current_app

from .models import Character

ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
assets.register('ts_coc', ts_coc)

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)

@bp.context_processor
def character_functions():
    def dict_path(data, path):       
        return reduce(lambda x,y : x[y], path.split("."), data)
    

    def get_skill(data, skillpath, subskill=None):
        path, skill = skillpath.split('#')
        skills = dict_path(data, path)
        for s in skills:
            if s['name'] == skill:
                if subskill is not None and subskill != s.get('subskill', 'None'):
                    print("Wrong subskill", skill, repr(subskill))
                    continue
                return s
    
        print("Did not find", skill, subskill)
        return 0
    
    return dict(dict_path=dict_path, get_skill=get_skill)


def get_character(id, check_author=True):
    character = Character.query.get(id)

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if check_author and character.user_id != current_user.id:
        abort(403)

    return character



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
            flash("Store character")
            c = Character(title=title, body=body, user_id=current_user.id)
            db.session.add(c)
            db.session.commit()
            return redirect(url_for('character.index'))
    
    return render_template('character/create.html.jinja', type=type)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    character = get_character(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
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
    data = get_character(id)

    character_data = json.loads(data.body)

    if not 'Investigator' in character_data:
        blank = render_template('character/blank_character.json.jinja')
        character_data = JsonComment(json).loads(blank)

    if request.method == "POST":
        update = request.get_json()

        for setting in update:
            if setting.get('type', None) == 'skill':
                path, skill = setting['field'].split('#')
                subfield = setting.get('subfield', None)
                value = setting.get('value')
                skills = reduce(lambda x,y : x[y], path.split("."), character_data['Investigator'])
                for s in skills:
                    if s['name'] == skill:
                        if subfield is not None and subfield != s.get('subskill', 'None'):
                            continue
                        s['value'] = value
                continue
        
            elif setting.get('type', None) == 'skillcheck':
                path, skill = setting['field'].split('#')
                subfield = setting.get('subfield', None)
                check = setting.get('value', False)
                skills = reduce(lambda x,y : x[y], path.split("."), character_data['Investigator'])
                for s in skills:
                    if s['name'] == skill:
                        if subfield is not None and subfield != s.get('subskill', 'None'):
                            continue
                        s['checked'] = check
                continue
            else:
                s = reduce(lambda x,y : x[y], setting['field'].split(".")[:-1], character_data['Investigator'])
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
    return render_template('character/sheet.html.jinja', character=character)

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
