from whathappened.core.auth.models import User
from whathappened.core.campaign.models import Campaign, CampaignCharacter
from whathappened.core.character.models import Character
from whathappened.models import UserProfile


def test_access_to_own_character(new_session):
    player = UserProfile()
    character = Character()
    character.player = player

    assert character.editable_by(player)
    assert character.viewable_by(player)


def test_access_as_gm(new_session):
    """Test access to character as GM."""
    player_user = User()
    player_user.username = "Player"

    player = UserProfile(user=player_user)

    gm_user = User()
    gm_user.username = "GM"

    gm = UserProfile(user=gm_user)

    new_session.add(player_user)
    new_session.add(gm_user)

    character = Character(title="Test character")
    character.player = player

    campaign = Campaign()
    campaign.user = gm

    assert not character.editable_by(gm)
    assert not character.viewable_by(gm)

    campaign_character = CampaignCharacter()
    campaign_character.character = character
    campaign.character_associations.append(campaign_character)

    assert not character.editable_by(gm)
    assert character.viewable_by(gm)

    campaign_character.editable_by_gm = True

    assert character.editable_by(gm)
    assert character.viewable_by(gm)


def test_access_as_player(new_session):
    """Test access to character as player in campaign."""
    player_user = User()
    player_user.username = "Player"

    player = UserProfile(user=player_user)

    other_player_user = User()
    other_player_user.username = "Other player"

    other_player = UserProfile(user=other_player_user)

    new_session.add(player_user)
    new_session.add(other_player_user)

    character = Character(title="Test character")
    character.player = player

    campaign = Campaign()

    assert not character.editable_by(other_player)
    assert not character.viewable_by(other_player)

    campaign_character = CampaignCharacter()
    campaign_character.character = character
    campaign.character_associations.append(campaign_character)

    # A player not in the same campaign should never have access.
    assert not character.editable_by(other_player)
    assert not character.viewable_by(other_player)

    campaign_character.group_sheet = True

    # A player not in the same campaign should never have access
    # when the sheet is shared either.
    assert not character.editable_by(other_player)
    assert not character.viewable_by(other_player)

    campaign.players.append(other_player)

    # A player in the same campaign should have both view and edit access
    # to a group sheet.
    assert character.editable_by(other_player)
    assert character.viewable_by(other_player)

    campaign_character.group_sheet = False

    # A player in the same campaign should not have any access
    # when the sheet is not shared.
    assert not character.editable_by(other_player)
    assert not character.viewable_by(other_player)

    campaign_character.editable_by_gm = True

    assert not character.editable_by(other_player)
    assert not character.viewable_by(other_player)

    campaign_character.share_with_players = True

    assert not character.editable_by(other_player)
    assert character.viewable_by(other_player)

    campaign_character.group_sheet = True
