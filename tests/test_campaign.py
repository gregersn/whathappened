import json
from app.campaign.models import Campaign


def test_create_campaign(db):
    campaign = Campaign(title='test_campaign')
    db.session.add(campaign)
    db.session.commit()

    campaigns = Campaign.query.all()
    assert campaign in campaigns
    assert str(campaign) == '<Campaign test_campaign>'


def test_api_hello(client):
    res = client.get('/api/campaign/hello/I_AM_TEST')
    assert res.status_code == 200, res.status_code
    assert res.headers.get('Content-Type') == 'application/json'
    assert json.loads(res.data) == {'msg': 'Hello, I_AM_TEST'}


def test_handout_players(client, auth, db):
    res = client.get('/api/campaign/1/handout/1/players')
    assert res.status_code == 403
