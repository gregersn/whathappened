from fastapi import Request


def flash(request: Request, error: str):
    """Recreate flash from Flask. 
    Store error message in "flashes" key of the session, so that all flashed messages can be displayed in a view."""

    request.session["flashes"] = request.session.get("flashes", []) + [error]
