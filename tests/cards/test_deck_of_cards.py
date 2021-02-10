from app.cards import load_deck


def test_read_cards():
    deck = load_deck("./tests/cards/test_deck.yaml")

    assert len(deck.cards) == 3
    assert deck.cards[0].text == "You won"
    assert deck.cards[2].text == "You lost"


def test_init_deck():
    deck = load_deck("./tests/cards/test_deck.yaml")

    assert len(deck.library) == 3
    assert deck.library[0].text == "You won"
    assert deck.library[2].text == "You lost"


def test_deal_card():
    deck = load_deck("./tests/cards/test_deck.yaml")

    card = deck.deal('tester')
    assert card.text == "You won"

    card = deck.deal('tester')
    assert card.text == "Try again"

    card = deck.deal('tester')
    assert card.text == "You lost"
