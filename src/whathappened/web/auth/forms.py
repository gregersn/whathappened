"""Authentication forms."""

from uuid import UUID
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from whathappened.core.database.models import Invite

from ...core.auth.models import User


class LoginForm(FlaskForm):
    """System login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """System registration form."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    invitation = StringField("Invitation code", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username: StringField):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email: StringField):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

    def validate_invitation(self, invitation: StringField):
        valid = True
        try:
            code = UUID(invitation.data)
        except ValueError:
            valid = False

        if valid:
            invite = Invite.query.filter_by(id=invitation.data).first()
            if invite is None:
                valid = False

        if not valid:
            raise ValidationError("Please use a valid invite code.")


class ResetPasswordRequestForm(FlaskForm):
    """Reset password request."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request password reset")


class ResetPasswordForm(FlaskForm):
    """Reset password form."""

    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request password reset")
