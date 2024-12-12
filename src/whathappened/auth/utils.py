from flask import render_template, current_app

from flask_login import (
    login_required as login_required,
    current_user as current_user,
    LoginManager as LoginManager,
)

from whathappened.auth.models import User
from whathappened.email import send_mail


def send_password_reset_email(user: User):
    token = user.get_reset_password_token()
    send_mail(
        "[What Happened?] Reset your password",
        sender=current_app.config["ADMINS"][0],
        recipients=[str(user.email)],
        text_body=render_template("/auth/reset_password.txt", user=user, token=token),
    )
