"""Authentication utility functions."""

from time import time
import jwt

from flask import render_template, current_app
from flask_login import login_required, current_user, LoginManager

from whathappened.core.auth.models import User
from whathappened.web.email import send_mail
from whathappened.core.database import session


__all__ = ["login_required", "current_user", "LoginManager"]


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
    """Send email to user with password reset token."""
    token = get_reset_password_token(user)
    send_mail(
        "[What Happened?] Reset your password",
        sender=current_app.config["ADMINS"][0],
        recipients=[str(user.email)],
        text_body=render_template("/auth/reset_password.txt", user=user, token=token),
    )
