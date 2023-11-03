import logging
from flask import flash, redirect, render_template, request, url_for

from flask_login import current_user, login_user, logout_user
from urllib.parse import urlsplit

from .forms import LoginForm, RegistrationForm
from .forms import ResetPasswordRequestForm, ResetPasswordForm
from .models import User

from whathappened.database import session

from . import bp, send_password_reset_email

logger = logging.getLogger(__name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next")
    if not next_page or urlsplit(next_page).netloc != "":
        next_page = url_for("main.index")

    if current_user.is_authenticated:
        logger.debug("User %s is already logged in", current_user.id)
        return redirect(next_page)
    form = LoginForm()
    if form.validate_on_submit():
        logger.debug("Login form was validated")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(next_page)
    return render_template("auth/login.html.jinja", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html.jinja", title="Register", form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for reset instructions.")
        return redirect(url_for("auth.login"))

    return render_template(
        "/auth/reset_password_request.html.jinja", title="Reset password", form=form
    )


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if user is not None:
            user.set_password(form.password.data)
        session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html.jinja", form=form)
