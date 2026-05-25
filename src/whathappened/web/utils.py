from litestar.response import Template

from whathappened.core.auth.utils import current_user


def render_template(template: str, **context):

    return Template(template, context={"current_user": current_user, **context})


def flash(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


def redirect(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


def url_for(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


def send_from_directory(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


class Blueprint:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(f"{args}, {kwargs}")
