import random

from card import Card


class Deck:
    """Клас Колоди карт."""

    def __init__(self, is_blackjack: bool = True):
        self._cards = []
        self._is_bj = is_blackjack
        self.build()

    def build(self) -> None:
        suits = ("♠", "♥", "♦", "♣")
        ranks = (
            ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] 
            if self._is_bj else ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        )
        self._cards = [Card(r, s) for s in suits for r in ranks]
        random.shuffle(self._cards)

    def draw(self) -> Card:
        return self._cards.pop() if self._cards else None