from .conftest import Conf as Config
from app import create_app

def test_config():
    assert not create_app().testing
    assert create_app(Config).testing

def test_hello():
    client = create_app(Config).test_client()
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
