import random
import unittest

from deck import Deck


def draw_all(deck):
    cards = []
    while True:
        card = deck.draw()
        if card is None:
            return cards
        cards.append(card.show())


class TestDeck(unittest.TestCase):
    def test_blackjack_deck_has_52_cards(self):
        self.assertEqual(len(draw_all(Deck(is_blackjack=True))), 52)

    def test_game_21_deck_has_36_cards_from_six_up(self):
        cards = draw_all(Deck(is_blackjack=False))
        self.assertEqual(len(cards), 36)
        for low in ("2", "3", "4", "5"):
            self.assertFalse(any(card.startswith(low) for card in cards))

    def test_all_cards_are_unique(self):
        cards = draw_all(Deck())
        self.assertEqual(len(set(cards)), len(cards))

    def test_draw_from_empty_deck_returns_none(self):
        deck = Deck(is_blackjack=False)
        draw_all(deck)
        self.assertIsNone(deck.draw())

    def test_works_without_injected_rng(self):
        self.assertEqual(len(draw_all(Deck())), 52)

    def test_same_seed_gives_same_order(self):
        first = draw_all(Deck(rng=random.Random(42)))
        second = draw_all(Deck(rng=random.Random(42)))
        self.assertEqual(first, second)

    def test_different_seeds_give_different_order(self):
        first = draw_all(Deck(rng=random.Random(1)))
        second = draw_all(Deck(rng=random.Random(2)))
        self.assertNotEqual(first, second)

    def test_injected_rng_is_the_one_used_for_shuffle(self):
        class SpyRng(random.Random):
            shuffles = 0
            def shuffle(self, x):
                SpyRng.shuffles += 1
                super().shuffle(x)

        Deck(rng=SpyRng(0))
        self.assertEqual(SpyRng.shuffles, 1)


if __name__ == "__main__":
    unittest.main()
