import math

from .. import bp


@bp.app_template_filter("half")
def half(value):
    if not value:
        return 0
    if type(value) == str:
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return math.floor(value / 2)


@bp.app_template_filter("fifth")
def fifth(value):
    if not value:
        return 0
    if type(value) == str:
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return math.floor(value / 5)
