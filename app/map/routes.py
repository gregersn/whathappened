from flask import render_template
from . import bp


@bp.route('/', methods=('GET', 'POST'))
def create():
    return render_template('map/maps.html.jinja')
