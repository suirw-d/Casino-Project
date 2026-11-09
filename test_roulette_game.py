import unittest

from casino import Casino
from fakes import FakeRng, make_io
from roulette_game import RouletteGame


def spin(number, choice, bet=10):
    """Один спін: кулька «випадає» на number, гравець обирає choice."""
    rng = FakeRng(number)
    game = RouletteGame(rng=rng)
    io, writer = make_io(choice)
    casino = Casino(io, games={})
    return game.play(casino, bet), writer, rng


class TestPayouts(unittest.TestCase):
    def test_zero_pays_14x(self):
        self.assertEqual(spin(0, "3", bet=10)[0], 140)

    def test_payout_scales_with_bet(self):
        self.assertEqual(spin(0, "3", bet=7)[0], 98)

    def test_red_pays_double(self):
        for number in (1, 3, 5):
            with self.subTest(number=number):
                self.assertEqual(spin(number, "1")[0], 20)

    def test_black_pays_double(self):
        for number in (2, 4, 6):
            with self.subTest(number=number):
                self.assertEqual(spin(number, "2")[0], 20)


class TestLosses(unittest.TestCase):
    def test_wrong_color_loses(self):
        self.assertEqual(spin(1, "2")[0], 0)
        self.assertEqual(spin(2, "1")[0], 0)

    def test_zero_beats_color_bets(self):
        self.assertEqual(spin(0, "1")[0], 0)
        self.assertEqual(spin(0, "2")[0], 0)

    def test_zero_bet_loses_on_other_numbers(self):
        self.assertEqual(spin(3, "3")[0], 0)

    def test_invalid_choice_loses(self):
        for choice in ("x", "", "7"):
            with self.subTest(choice=choice):
                self.assertEqual(spin(1, choice)[0], 0)

    def test_losing_spin_prints_message(self):
        self.assertIn("не співпали", spin(1, "2")[1].text)


class TestBehaviour(unittest.TestCase):
    def test_choice_is_stripped(self):
        self.assertEqual(spin(1, " 1 ")[0], 20)

    def test_rng_is_asked_for_number_from_0_to_6(self):
        _, _, rng = spin(4, "2")
        self.assertEqual(rng.calls, [(0, 6)])

    def test_result_message_shows_number_and_color(self):
        self.assertIn("5 (Червоне)", spin(5, "1")[1].text)
        self.assertIn("4 (Чорне)", spin(4, "2")[1].text)
        self.assertIn("Зеро (0)", spin(0, "3")[1].text)

    def test_rules_are_printed(self):
        self.assertIn("ПРАВИЛА РУЛЕТКИ", spin(1, "1")[1].text)

    def test_get_rules_mentions_x14(self):
        self.assertIn("x14", RouletteGame().get_rules())

    def test_default_rng_works_without_injection(self):
        io, _ = make_io("1")
        payout = RouletteGame().play(Casino(io, games={}), 10)
        self.assertIn(payout, (0, 20))


if __name__ == "__main__":
    unittest.main()
