from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from .forms import LoginForm, RegistrationForm
from .models import User

from app import db

from . import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')

    print("Logging in!")
    if current_user.is_authenticated:
        print("User is already logged in")
        return redirect(next_page)
    form = LoginForm()
    if form.validate_on_submit():
        print("Login form was validated")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(next_page)
    return render_template('auth/login.html.jinja', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html.jinja', title='Register', form=form)
