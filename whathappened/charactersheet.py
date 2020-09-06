from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from whathappened.auth import login_required
from whathappened.db import get_db

bp = Blueprint('character', __name__)

@bp.route('/')
def index():
    db = get_db()
    characters = db.execute(
        'SELECT c.id, title, body, author_id, created, username'
        ' FROM character c JOIN user u ON c.author_id = u.id'
        ' ORDER BY CREATED DESC'
    ).fetchall()

    return render_template('character/index.html.jinja', characters=characters)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO character (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('character.index'))
    
    return render_template('character/create.html.jinja')

def get_character(id, check_author=True):
    character = get_db().execute(
        'SELECT c.id, title, body, created, author_id, username'
        ' FROM character c JOIN user u ON c.author_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if character is None:
        abort(404, "Character id {0} doesn't exist.".format(id))

    if check_author and character['author_id'] != g.user['id']:
        abort(403)

    return character

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
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
            db = get_db()
            db.execute(
                'UPDATE character SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('character.index'))
    
    return render_template('character/update.html.jinja', character=character)

@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_character(id)
    db = get_db()
    db.execute('DELETE FROM character WHERE id = ?', (id, ))
    db.commit()
    return redirect(url_for('character.index'))
