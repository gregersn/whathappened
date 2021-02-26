import yaml
import random
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Card:
    text: str
    revealed: bool
    pile: List['Card']

    def __init__(self, data: dict, deck):
        self.deck = deck
        self.text = data['text']
        self.revealed = False

    def discard(self):
        self.deck.discard(self)

    def give_to(self, to: str):
        self.deck.move(self, to)

    def reveal(self):
        self.revealed = True

    def hide(self):
        self.revealed = False

    def to_dict(self, show_hidden=False):
        return {
            'text': self.text if show_hidden or self.revealed else None
        }


class Deck:
    cards: List[Card]
    library: List[Card]
    piles: Dict[str, List[Card]]
    discard: List[Card]
    table: List[Card]

    def __init__(self, data: dict):
        self.cards = [Card(c, self) for c in data['cards']]
        self.reset()

    def reset(self):
        self.library = self.cards.copy()
        self.piles = {}
        self.discard = []
        self.table = []

    def reset_discard(self):
        self.library = self.library + self.discard
        for card in self.library:
            card.pile = self.library
        self.discard = []

    def shuffle(self):
        random.shuffle(self.library)

    def deal(self, to: str) -> Card:
        card = self.library.pop(0)
        if to not in self.piles:
            self.piles[to] = []
        card.pile = self.piles[to]
        self.piles[to].append(card)
        return card

    def hand(self, name: str) -> List[Card]:
        if name in self.piles:
            return self.piles[name]

        return []

    def move(self, card: Card, to: str) -> Card:
        if card.pile is not None:
            card.pile.remove(card)

        if to not in self.piles:
            self.piles[to] = []

        card.pile = self.piles[to]
        self.piles[to].append(card)

        return card

    def state(self, show_hidden=False):
        return {
            'library': [c.to_dict(show_hidden) for c in self.library],
            'discard': [c.to_dict(show_hidden) for c in self.discard],
            'piles': {
                        name: [c.to_dict(show_hidden) for c in pile]
                        for name, pile in self.piles.items()
                    }
        }


def load_deck(filename: str) -> Deck:
    with open(filename, 'r') as f:
        deck = yaml.safe_load(f)
    return Deck(deck)
