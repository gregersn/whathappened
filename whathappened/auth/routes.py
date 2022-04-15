import logging
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from whathappened.utils import flash
from whathappened.environment import templates

from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html.jinja", {"request": request, "form": RegistrationForm()})


@router.post("/register")
def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    """Register a new user."""

    error = None

    # Try to get the user by username, to check if it is already registered.

    if error is None:
        # Hash the password
        # Create the user
        # Return redirect to login.
        return RedirectResponse("/auth/login", status_code=302)
    else:
        # Error - redirect back to register page.
        flash(request, error)
        return RedirectResponse("/auth/register", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html.jinja", {"request": request, "form": LoginForm()})


@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """Login user."""

    # Find user

    return RedirectResponse("/hello", status_code=302)


@router.get('/reset_password_request')
def reset_password_request(request: Request):
    form = ResetPasswordRequestForm()
    return templates.TemplateResponse('auth/reset_password_request.html.jinja', {
        'request': request,
        'title': 'Reset password',
        'form': form
    })


@router.post('/reset_password_request')
def reset_password(request: Request, email: str = Form(...)):
    user = User.query.filter_by(email=form.email.data).first()
    if user:
        send_password_reset_email(user)
    flash('Check your email for reset instructions.')
    return redirect(url_for('auth.login'))


@router.get('/reset_password/<token>')
def reset_password_form():
    user = User.verify_reset_password_token(token)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if user is not None:
            user.set_password(form.password.data)
        session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html.jinja', form=form)


@router.post("/reset_password/<token>")
def reset_password(token: str = Form(...)):
    pass