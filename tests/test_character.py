import pytest


@pytest.mark.parametrize('path', (
    '/',
))
def test_login_required(client, path):
    response = client.get(path)
    assert 'http://localhost/auth/login' in response.headers['Location']



@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

