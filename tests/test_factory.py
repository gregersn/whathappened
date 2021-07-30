from .conftest import Conf as Config
from whathappened import create_app, assets


def test_config(app):
    assets._named_bundles = {}
    a = create_app()

    assert not a.testing, a.testing

    assets._named_bundles = {}

    assert Config.TESTING is True

    a = create_app(Config)
    assert a.testing, a.testing


def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
