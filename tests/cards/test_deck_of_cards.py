import pytest
from app.cards import load_deck


@pytest.fixture
def deck():
    return load_deck("./tests/cards/test_deck.yaml")


def test_read_cards(deck):
    assert len(deck.cards) == 3
    assert deck.cards[0].text == "You won"
    assert deck.cards[2].text == "You lost"


def test_init_deck(deck):
    assert len(deck.library) == 3
    assert deck.library[0].text == "You won"
    assert deck.library[2].text == "You lost"


def test_deal_card(deck):
    assert len(deck.library) == 3
    assert len(deck.hand('tester')) == 0
    card = deck.deal('tester')
    assert card.text == "You won"
    assert card.pile is deck.hand('tester')

    assert len(deck.library) == 2
    assert len(deck.hand('tester')) == 1
    card = deck.deal('tester')
    assert card.text == "Try again"
    assert card.pile is deck.hand('tester')

    assert len(deck.library) == 1
    assert len(deck.hand('tester')) == 2
    card = deck.deal('tester')
    assert card.text == "You lost"
    assert card.pile is deck.hand('tester')

    assert len(deck.library) == 0
    assert len(deck.hand('tester')) == 3


def test_give_card(deck):
    card = deck.deal('tester')
    assert len(deck.hand('tester')) == 1

    card.give_to('tester2')

    assert len(deck.hand('tester2')) == 1
    assert len(deck.hand('tester')) == 0


def test_deck_state(deck):
    state = deck.state()
    assert state == {
        'discard': [],
        'library': [
            {'text': None},
            {'text': None},
            {'text': None}
        ],
        'piles': {}
    }

    state = deck.state(show_hidden=True)
    assert state == {
        'discard': [],
        'library': [
            {'text': "You won"},
            {'text': "Try again"},pile
        ],
        'piles': {}
    }

    deck.deal('player1')

    state = deck.state()
    assert state == {
        'discard': [],
        'library': [
            {'text': None},
            {'text': None}
        ],
        'piles': {
            'player1': [
                {'text': None}
            ]
        }
    }

    state = deck.state(show_hidden=True)
    assert state == {
        'discard': [],
        'library': [
            {'text': "Try again"},
            {'text': "You lost"}
        ],
        'piles': {
            'player1': [
                {'text': "You won"}
            ]
        }
    }
