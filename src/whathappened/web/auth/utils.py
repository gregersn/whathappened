from time import time

from flask import current_app, render_template
from flask_login import (
    LoginManager as LoginManager,
)
from flask_login import (
    current_user as current_user,
)
from flask_login import (
    login_required as login_required,
)
import jwt

from whathappened.core.auth.models import User
from whathappened.core.database import session
from whathappened.web.email import send_mail


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
