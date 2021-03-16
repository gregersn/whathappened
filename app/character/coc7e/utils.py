from typing import Union
from .. import bp


@bp.app_template_filter('half')
def half(value: Union[str, int]):
    if not value:
        return 0
    if isinstance(value, str):
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return value // 2


@bp.app_template_filter('fifth')
def fifth(value: Union[str, int]):
    if not value:
        return 0
    if isinstance(value, str):
        try:
            value = int(value, 10)
        except ValueError:
            return 0
    return value // 5
