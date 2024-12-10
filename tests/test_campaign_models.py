from whathappened.campaign.models import Campaign, NPC
from whathappened.models import UserProfile
from whathappened.character.models import Character


def test_create_campaign(db):
    campaign = Campaign(title="test_campaign")
    db.session.add(campaign)
    db.session.commit()

    campaigns = Campaign.query.all()
    assert campaign in campaigns
    assert str(campaign) == "<Campaign test_campaign>"


def test_campaign_player_list(db):
    campaign = Campaign(title="test_campaign")
    player1 = UserProfile()

    campaign.players.add(player1)

    assert campaign.players_by_id == {None: player1}


def test_campaign_npc_list(db):
    campaign = Campaign(title="test_campaign")
    character1 = Character(title="test_character")
    assert not campaign.NPCs.all()

    campaign.npcs_enabled = True

    npc = NPC(character=character1, campaign=campaign)

    assert npc in list(campaign.NPCs.all())
    assert npc in list(character1.npc)
