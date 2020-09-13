import unittest
from app import create_app, db
from .support import Conf as Config
import pytest
from flask import g, session


from app.auth.forms import RegistrationForm

def test_register(app, db):
    client = app.test_client()
    assert client.get('/auth/register').status_code == 200

    response = client.post(
        '/auth/register', data={'username': 'a', 'email': 't@t.com', 'password': 'b', 'password2': 'b'}
    )
    assert 'http://localhost/auth/login' ==  response.headers['Location']


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
