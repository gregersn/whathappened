from app.campaign.models import Campaign


def test_create_campaign(db):
    campaign = Campaign(title='test_campaign')
    db.session.add(campaign)
    db.session.commit()

    campaigns = Campaign.query.all()
    assert campaign in campaigns
    assert str(campaign) == '<Campaign test_campaign>'
