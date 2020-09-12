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

ts_coc = Bundle("ts/coc.ts", filters='typescript', output='js/coc.js')
assets.register('ts_coc', ts_coc)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': json.loads(self.body),
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }

bp = Blueprint('character', __name__)
api = Blueprint('characterapi', __name__)

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

    return render_template('character/index.html.jinja', characters=characters)

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
        # print(blank)
        character_data = JsonComment(json).loads(blank)

    if request.method == "POST":
        update = request.get_json()
        for key, value in update.items():
            print(key, value)
            s = reduce(lambda x,y : x[y], key.split(".")[:-1], character_data['Investigator'])
            s[key.split(".")[-1]] = value
        
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
