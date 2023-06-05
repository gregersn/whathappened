from whathappened.campaign.models import Campaign
from whathappened.models import UserProfile


def test_create_campaign(db):
    campaign = Campaign(title='test_campaign')
    db.session.add(campaign)
    db.session.commit()

    campaigns = Campaign.query.all()
    assert campaign in campaigns
    assert str(campaign) == '<Campaign test_campaign>'


def test_campaing_player_list(db):
    campaign = Campaign(title="test_campaign")
    player1 = UserProfile()

    campaign.players.add(player1)

    assert campaign.players_by_id == {None: player1}
