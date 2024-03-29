from .conftest import Config
from whathappened import create_app, assets


def test_config(app):
    assets._named_bundles = {}
    a = create_app()

    assert not a.testing

    assets._named_bundles = {}

    a = create_app(Config)
    assert a.testing


def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
