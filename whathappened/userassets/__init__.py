from flask import Blueprint
from flask import url_for

bp = Blueprint('userassets', __name__ )
apibp = Blueprint('userassetsapi', __name__ )

from . import routes  # noqa: F401,E402 isort:skip
# from . import views  # noqa: F401, E402 isort:skip
# from . import api  # noqa: F401, E402 isort:skip


@bp.app_template_filter('clickpath')
def clickpath(folder):
    path = ""
    if folder.parent:
        path = clickpath(folder.parent)

    folder_link = """<a href="{}">{}</a>"""
    folder_url = url_for('userassets.index', folder_id=folder.id)
    return path + "/" + folder_link.format(folder_url, folder.title)
