import unittest

from card import Card
from hand import Hand


def make_hand(*ranks: str, name: str = "Гравець") -> Hand:
    """Допоміжна функція: створює руку з картами заданих рангів."""
    hand = Hand(name)
    for rank in ranks:
        hand.add_card(Card(rank, "♠"))
    return hand


class TestHandBasics(unittest.TestCase):
    def test_name_is_stored(self):
        self.assertEqual(Hand("Дилер").name, "Дилер")

    def test_new_hand_is_empty(self):
        self.assertEqual(Hand("Гравець").cards, [])


class TestAddCard(unittest.TestCase):
    def test_add_card_appends_card(self):
        hand = Hand("Гравець")
        card = Card("K", "♥")
        hand.add_card(card)
        self.assertEqual(hand.cards, [card])

    def test_add_multiple_cards_keeps_order(self):
        hand = Hand("Гравець")
        first, second = Card("2", "♠"), Card("A", "♦")
        hand.add_card(first)
        hand.add_card(second)
        self.assertEqual(hand.cards, [first, second])

    def test_add_none_is_ignored(self):
        hand = Hand("Гравець")
        with self.assertLogs("hand", level="WARNING"):
            hand.add_card(None)
        self.assertEqual(hand.cards, [])

    def test_add_card_logs_rank_and_suit(self):
        hand = Hand("Дилер")
        with self.assertLogs("hand", level="INFO") as logs:
            hand.add_card(Card("Q", "♣"))
        message = logs.output[0]
        self.assertIn("Дилер", message)
        self.assertIn("Q", message)
        self.assertIn("♣", message)

    def test_add_none_logs_warning(self):
        hand = Hand("Гравець")
        with self.assertLogs("hand", level="WARNING") as logs:
            hand.add_card(None)
        self.assertIn("WARNING", logs.output[0])


class TestGetScore(unittest.TestCase):
    def test_empty_hand_scores_zero(self):
        self.assertEqual(Hand("Гравець").get_score(), 0)

    def test_simple_sum(self):
        self.assertEqual(make_hand("5", "7").get_score(), 12)

    def test_face_cards_count_as_ten(self):
        self.assertEqual(make_hand("J", "Q").get_score(), 20)
        self.assertEqual(make_hand("K", "10").get_score(), 20)

    def test_ace_counts_as_eleven_when_safe(self):
        self.assertEqual(make_hand("A", "5").get_score(), 16)

    def test_ace_and_king_is_twenty_one(self):
        self.assertEqual(make_hand("A", "K").get_score(), 21)

    def test_ace_drops_to_one_on_bust(self):
        # 11 + 9 + 5 = 25 -> 15
        self.assertEqual(make_hand("A", "9", "5").get_score(), 15)

    def test_two_aces_score_twelve(self):
        self.assertEqual(make_hand("A", "A").get_score(), 12)

    def test_two_aces_and_nine_is_twenty_one(self):
        self.assertEqual(make_hand("A", "A", "9").get_score(), 21)

    def test_three_aces_score_thirteen(self):
        self.assertEqual(make_hand("A", "A", "A").get_score(), 13)

    def test_bust_without_aces(self):
        self.assertEqual(make_hand("K", "Q", "5").get_score(), 25)

    def test_bust_even_after_all_aces_reduced(self):
        # 1 + 1 + 10 + 10 = 22, туз уже не може допомогти
        self.assertEqual(make_hand("A", "A", "K", "Q").get_score(), 22)

    def test_score_does_not_modify_cards(self):
        hand = make_hand("A", "9", "5")
        hand.get_score()
        self.assertEqual(hand.get_score(), 15)
        self.assertEqual(len(hand.cards), 3)


if __name__ == "__main__":
    unittest.main()