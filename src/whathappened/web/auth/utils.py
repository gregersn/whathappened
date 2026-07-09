from functools import wraps
from time import time

from litestar import Request

from whathappened.core.auth.models import User
from whathappened.core.auth.utils import current_user
from whathappened.core.database import session
from whathappened.web.email import send_mail


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def get_reset_password_token(user: User, expires_in: int = 600):
    """Create token for password reset."""
    return jwt.encode(
        {"reset_password": user.id, "exp": time() + expires_in},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def verify_reset_password_token(token: str):
    """Verify password reset token."""
    user_id = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])[
        "reset_password"
    ]
    return session.get(User, user_id)


def send_password_reset_email(user: User):
    token = get_reset_password_token(user)
    send_mail(
        "[What Happened?] Reset your password",
        sender=current_app.config["ADMINS"][0],
        recipients=[str(user.email)],
        text_body=render_template("/auth/reset_password.txt", user=user, token=token),
    )


def login_user(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


def logout_user(*args, **kwargs):
    raise NotImplementedError(f"{args}, {kwargs}")


def provide_user(request: Request):
    # current_user.clear()
    if "session" in request.scope:
        print("User is in request scope")
        return request.user
