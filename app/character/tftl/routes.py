
from flask import render_template


def view(id, character, editable):
    return render_template('character/tftl/sheet.html.jinja',
                           character=character,
                           editable=editable)
