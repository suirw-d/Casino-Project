import unittest

from card_game import CardGame
from casino import Casino
from fakes import make_io, stacked_factory


def play(ranks, answers, bet=10, blackjack=True):
    """Одна гра з наперед заданою колодою.

    ranks — порядок видачі карт: гравець, дилер, гравець, дилер (і третя карта гравцю, якщо бере).
    """
    factory = stacked_factory(*ranks)
    game = CardGame("Тест", is_blackjack=blackjack, deck_factory=factory)
    io, writer = make_io(*answers)
    casino = Casino(io, games={})
    return game.play(casino, bet), writer, factory


def simulate(ranks, rounds, bet=10, balance=100):
    """Симуляція: у кожному раунді карти йдуть у порядку: гравець, гравець, дилер, дилер."""
    factory = stacked_factory(*ranks)
    game = CardGame("Тест", is_blackjack=True, deck_factory=factory)
    io, writer = make_io()
    casino = Casino(io, games={}, initial_balance=balance)
    game.simulate(casino, bet, rounds)
    return casino, writer, factory


class TestRules(unittest.TestCase):
    def test_blackjack_rules_mention_52_cards(self):
        self.assertIn("52", CardGame("Б", is_blackjack=True).get_rules())

    def test_game_21_rules_mention_36_cards(self):
        self.assertIn("36", CardGame("2", is_blackjack=False).get_rules())


class TestPlay(unittest.TestCase):
    def test_win_pays_double(self):
        # гравець K+9=19, дилер 7+8=15
        payout, writer, _ = play(["K", "7", "9", "8"], ["0"], bet=10)
        self.assertEqual(payout, 20)
        self.assertIn("Виграш", writer.text)

    def test_tie_returns_bet(self):
        # 10+8=18 проти 9+9=18
        payout, writer, _ = play(["10", "9", "8", "9"], ["0"], bet=10)
        self.assertEqual(payout, 10)
        self.assertIn("Нічия", writer.text)

    def test_loss_pays_zero(self):
        # 10+7=17 проти K+9=19
        payout, writer, _ = play(["10", "K", "7", "9"], ["0"])
        self.assertEqual(payout, 0)
        self.assertIn("Програш", writer.text)

    def test_hit_can_turn_into_win(self):
        # 5+6=11, бере 10 -> 21; дилер 10+10=20
        payout, _, _ = play(["5", "10", "6", "10", "10"], ["1"], bet=10)
        self.assertEqual(payout, 20)

    def test_bust_after_hit_loses_even_if_dealer_is_low(self):
        # K+Q=20, бере K -> 30; дилер 2+3=5
        payout, _, _ = play(["K", "2", "Q", "3", "K"], ["1"])
        self.assertEqual(payout, 0)

    def test_answer_is_stripped(self):
        payout, _, _ = play(["5", "10", "6", "10", "10"], [" 1 "])
        self.assertEqual(payout, 20)

    def test_pass_does_not_draw_third_card(self):
        _, writer, _ = play(["K", "7", "9", "8", "2"], ["0"])
        shown = [line for line in writer.lines if "Ваші карти" in line]
        self.assertEqual(len(shown), 1)

    def test_hit_shows_hand_again(self):
        _, writer, _ = play(["5", "10", "6", "10", "10"], ["1"])
        shown = [line for line in writer.lines if "Ваші карти" in line]
        self.assertEqual(len(shown), 2)

    def test_dealer_cards_are_shown(self):
        _, writer, _ = play(["K", "7", "9", "8"], ["0"])
        self.assertIn("Карти дилера", writer.text)

    def test_two_aces_are_scored_by_hand_rules(self):
        # гравець A+A=12, дилер 8+3=11 -> перемога
        payout, _, _ = play(["A", "8", "A", "3"], ["0"], bet=10)
        self.assertEqual(payout, 20)

    def test_deck_factory_gets_blackjack_flag(self):
        _, _, factory = play(["K", "7", "9", "8"], ["0"], blackjack=False)
        self.assertEqual(factory.calls, [False])

    def test_every_game_gets_a_fresh_deck(self):
        factory = stacked_factory("K", "7", "9", "8")
        game = CardGame("Тест", deck_factory=factory)
        for _ in range(2):
            io, _ = make_io("0")
            game.play(Casino(io, games={}), 10)
        self.assertEqual(len(factory.calls), 2)


class TestSimulate(unittest.TestCase):
    WIN = ["K", "9", "7", "8"]    # 19 проти 15
    LOSS = ["7", "8", "K", "9"]   # 15 проти 19
    TIE = ["K", "8", "9", "9"]    # 18 проти 18

    def test_all_wins(self):
        casino, writer, _ = simulate(self.WIN, rounds=3)
        self.assertEqual(casino.balance, 130)
        self.assertIn("Перемог: 3 | Поразок: 0 | Нічій: 0", writer.text)
        self.assertIn("+$30", writer.text)

    def test_all_losses(self):
        casino, writer, _ = simulate(self.LOSS, rounds=3)
        self.assertEqual(casino.balance, 70)
        self.assertIn("Перемог: 0 | Поразок: 3 | Нічій: 0", writer.text)
        self.assertIn("$-30", writer.text)

    def test_all_ties_keep_balance(self):
        casino, writer, _ = simulate(self.TIE, rounds=3)
        self.assertEqual(casino.balance, 100)
        self.assertIn("Перемог: 0 | Поразок: 0 | Нічій: 3", writer.text)

    def test_stops_when_balance_is_not_enough_for_bet(self):
        casino, writer, _ = simulate(self.LOSS, rounds=5, bet=10, balance=25)
        self.assertEqual(casino.balance, 5)
        self.assertIn("Зіграно раундів: 2", writer.text)
        self.assertIn("Баланс вичерпано", writer.text)

    def test_zero_rounds_plays_nothing(self):
        casino, writer, factory = simulate(self.WIN, rounds=0)
        self.assertEqual(casino.balance, 100)
        self.assertEqual(factory.calls, [])
        self.assertIn("Зіграно раундів: 0", writer.text)

    def test_new_deck_every_round(self):
        _, _, factory = simulate(self.WIN, rounds=4)
        self.assertEqual(len(factory.calls), 4)

    @unittest.expectedFailure
    def test_two_aces_are_scored_like_in_play(self):
        # Відома розбіжність: simulate() додає get_value() без правила тузів
        # (A+A = 22 -> перебір), а play() через Hand рахує A+A = 12.
        # Гравець A+A проти дилера 8+3 у play() виграє, а в simulate() програє.
        # Коли розбіжність виправлять, цей тест почне «несподівано проходити»
        # і його треба буде зняти з expectedFailure.
        casino, _, _ = simulate(["A", "A", "8", "3"], rounds=1, bet=10, balance=100)
        self.assertEqual(casino.balance, 110)


if __name__ == "__main__":
    unittest.main()
