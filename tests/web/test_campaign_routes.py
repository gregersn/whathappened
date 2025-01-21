import json


def test_api_hello(client):
    res = client.get("/api/campaign/hello/I_AM_TEST")
    assert res.status_code == 200, res.status_code
    assert res.headers.get("Content-Type") == "application/json"
    assert json.loads(res.data) == {"msg": "Hello, I_AM_TEST"}


def test_handout_players(client, auth, db):
    res = client.get("/api/campaign/1/handout/1/players")
    assert res.status_code == 403


def test_campaign_view(authorized_client, auth, db):
    res = authorized_client.get("/campaign/1", follow_redirects=True)
    assert res.status_code in [200], res.status_code
    assert res.headers.get("Content-Type") == "text/html; charset=utf-8"
