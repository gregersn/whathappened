def test_empty_db(client):
    rv = client.get('/')
    assert b'you must register' in rv.data
