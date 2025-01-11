from whathappened.web import create_app
from ..conftest import Conf
from whathappened import assets


def test_config():
    assets._named_bundles = {}

    a = create_app(Conf())
    assert a.testing

    Config = Conf()
    Config.TESTING = False
    assets._named_bundles = {}
    a = create_app(Config)

    assert not a.testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"
