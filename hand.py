import logging

from card import Card

logger = logging.getLogger(__name__)


class Hand:
    """Клас Руки гравця/дилера."""

    def __init__(self, name: str):
        self._name = name
        self._cards = []
        self._ranks_set = set()
        logger.debug("Створено руку '%s'", self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def cards(self) -> list:
        return self._cards

    def add_card(self, card: Card) -> None:
        if card:
            self._cards.append(card)
            self._ranks_set.add(card.rank)
            logger.info("Рука '%s': видано карту %s %s (карт на руці: %s)",
                        self._name, card.rank, card.suit, len(self._cards))
        else:
            logger.warning("Рука '%s': спроба додати порожню карту (%r)", self._name, card)

    def get_score(self) -> int:
        total = sum(c.get_value() for c in self._cards)
        aces = sum(1 for c in self._cards if c.rank == "A")
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        logger.debug("Рука '%s': рахунок %s", self._name, total)
        return total