import yaml
import random
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Card:
    text: str

    def __init__(self, data: dict):
        self.text = data['text']


class Deck:
    cards: List[Card]
    library: List[Card]
    piles: Dict[str, List[Card]]

    def __init__(self, data: dict):
        self.cards = [Card(c) for c in data['cards']]
        self.reset()

    def reset(self):
        self.library = self.cards.copy()
        self.piles = {}

    def shuffle(self):
        random.shuffle(self.library)

    def deal(self, to) -> Card:
        card = self.library.pop(0)
        if to not in self.piles:
            self.piles[to] = []
        self.piles[to].append(card)
        return card

    def hand(self, name) -> List[Card]:
        if name in self.piles:
            return self.piles[name]

        return []


def load_deck(filename: str) -> Deck:
    with open(filename, 'r') as f:
        deck = yaml.safe_load(f)
    return Deck(deck)
