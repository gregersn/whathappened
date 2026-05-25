"""Auth routes."""

from litestar.response.redirect import Redirect


import logging
from typing import Any
from urllib.parse import urlsplit

from litestar import HttpMethod, Request, Response, get, route
from litestar.enums import RequestEncodingType
from litestar.handlers import post
from litestar.params import Body
from litestar.response import Redirect, Template
from litestar.router import Router
from litestar.template.base import url_for
from werkzeug.wrappers.response import Response

from whathappened.config import Config
from whathappened.core.auth.utils import current_user
from whathappened.core.database import session
from whathappened.web.utils import render_template

from ...core.auth.models import User, UserStatus
from .forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from .utils import (
    login_user,
    send_password_reset_email,
    verify_reset_password_token,
)

logger = logging.getLogger(__name__)


@get("/login")
async def login() -> Template:
    form = LoginForm()
    return render_template("auth/login.html.jinja", title="Sign In", form=form)


@post("/login")
async def login_POST(
    request: Request,
    data: Any = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> Response | Redirect:
    """Login route."""
    # next_page = data.query_params.get("next")
    # if not next_page or urlsplit(next_page).netloc != "":
    #    next_page = "/index"

    # if current_user.is_authenticated:
    #     logger.debug("User %s is already logged in", current_user.id)
    #    return Redirect(next_page)
    form = LoginForm(data=data)
    if form.validate():
        logger.debug("Login form was validated")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            raise NotImplementedError('flash("Invalid username or password")')
            return Redirect("/auth/login")
        # login_user(user, remember=form.remember_me.data)
        request.set_session({"username": user.username})
        current_user.set_user(user)

        user.status = UserStatus.active
        session.add(user)
        session.commit()

    return Redirect("/")


@get("/logout")
async def logout(request: Request) -> Redirect:
    """Logout route."""
    request.clear_session()
    current_user.clear()
    return Redirect("/")


@get("/register")
async def register() -> Template:
    """Register new user route."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    return render_template(
        "auth/register.html.jinja",
        title="Register",
        form=form,
        current_user=current_user,
    )


@post("/register")
async def register_POST(
    data: Any = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> Response | Redirect:
    form = RegistrationForm(data=data)

    form.validate()

    if not form.errors and not Config.REQUIRE_INVITE:
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        flash("Congratulations, you are now a registered user!")
        return Redirect("/auth/login")

    if (
        Config.REQUIRE_INVITE
        and len(form.errors.keys()) == 1
        and "email" in form.errors.keys()
    ):
        user = (
            User.query.filter_by(username=form.email.data)
            .filter_by(status=UserStatus.invited)
            .first()
        )
        if user is not None:
            user.username = form.username.data
            user.status = UserStatus.registered
            user.set_password(form.password.data)

            session.add(user)
            session.commit()
            flash("Congratulations, you are now a registered user!")
            return Redirect("/auth/login")

    if current_app.config.get("REQUIRE_INVITE"):
        if not form.email.errors:
            form.email.errors = []
        form.email.errors.append("Invitation needed to register.")


@get("/reset_password_request", methods=["GET", "POST"])
async def reset_password_request():
    """Reset password request route."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ResetPasswordRequestForm()
    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for reset instructions.")
        return redirect(url_for("auth.login"))

    return render_template(
        "/auth/reset_password_request.html.jinja", title="Reset password", form=form
    )


@get("/reset_password/<token>", methods=["GET", "POST"])
async def reset_password(token: str):
    """Reset password route."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = verify_reset_password_token(token)
    form = ResetPasswordForm()
    if form.validate():
        if user is not None:
            user.set_password(form.password.data)
        session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html.jinja", form=form)


auth_router = Router(
    path="/auth", route_handlers=[login, login_POST, logout, register, register_POST]
)
