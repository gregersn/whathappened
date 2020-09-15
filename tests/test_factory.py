from .conftest import Conf as Config
from app import create_app, assets

def test_config(app):
    assets._named_bundles = {}
    assert not create_app().testing
    assets._named_bundles = {}
    assert create_app(Config).testing

def test_hello():
    assets._named_bundles = {}
    client = create_app(Config).test_client()
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
