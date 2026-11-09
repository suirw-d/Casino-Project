import unittest

from casino import Casino
from fakes import FakeGame, make_io


class FakeCardGame(FakeGame):
    """Гра-заглушка, яка вміє ще й simulate()."""

    def __init__(self, payout=0, name="fake"):
        super().__init__(payout, name)
        self.simulations = []

    def simulate(self, casino, bet, rounds):
        self.simulations.append((bet, rounds))


def new_casino(*answers, games=None, balance=500):
    io, writer = make_io(*answers)
    return Casino(io, games if games is not None else {}, initial_balance=balance), writer


class TestBalance(unittest.TestCase):
    def test_default_balance(self):
        io, _ = make_io()
        self.assertEqual(Casino(io, {}).balance, 500)

    def test_add_balance(self):
        casino, _ = new_casino()
        casino.add_balance(50)
        self.assertEqual(casino.balance, 550)

    def test_add_zero_or_negative_is_ignored(self):
        casino, _ = new_casino()
        casino.add_balance(0)
        casino.add_balance(-10)
        self.assertEqual(casino.balance, 500)

    def test_deduct_balance(self):
        casino, _ = new_casino()
        casino.deduct_balance(120)
        self.assertEqual(casino.balance, 380)

    def test_deduct_more_than_balance_is_rejected(self):
        casino, _ = new_casino()
        casino.deduct_balance(501)
        self.assertEqual(casino.balance, 500)

    def test_deduct_zero_or_negative_is_rejected(self):
        casino, _ = new_casino()
        casino.deduct_balance(0)
        casino.deduct_balance(-5)
        self.assertEqual(casino.balance, 500)


class TestGetBet(unittest.TestCase):
    def test_valid_bet(self):
        casino, _ = new_casino("50")
        self.assertEqual(casino.get_bet(), 50)

    def test_invalid_bets_fall_back_to_minimum(self):
        for answer in ("abc", "", "0", "-5", "9999"):
            with self.subTest(answer=answer):
                casino, _ = new_casino(answer)
                self.assertEqual(casino.get_bet(), 10)

    def test_minimum_never_exceeds_balance(self):
        casino, _ = new_casino("abc", balance=5)
        self.assertEqual(casino.get_bet(), 5)

    def test_invalid_bet_prints_message(self):
        casino, writer = new_casino("-5")
        casino.get_bet()
        self.assertIn("Некоректна сума", writer.text)


class TestMenuWithInjectedGames(unittest.TestCase):
    def test_winning_game_updates_balance(self):
        game = FakeGame(payout=200)
        casino, _ = new_casino("3", "100", "0", games={"roulette": game})
        casino.menu()
        self.assertEqual(game.bets, [100])
        self.assertEqual(casino.balance, 600)

    def test_menu_choice_selects_the_right_game(self):
        games = {"21": FakeGame(name="a"), "bj": FakeGame(name="b"), "roulette": FakeGame(name="c")}
        casino, _ = new_casino("2", "10", "0", games=games)
        casino.menu()
        self.assertEqual(games["21"].bets, [])
        self.assertEqual(games["bj"].bets, [10])
        self.assertEqual(games["roulette"].bets, [])

    def test_session_summary_counts_results(self):
        cases = {200: "Перемог: 1 | Поразок: 0 | Нічій: 0",
                 0: "Перемог: 0 | Поразок: 1 | Нічій: 0",
                 100: "Перемог: 0 | Поразок: 0 | Нічій: 1"}
        for payout, expected in cases.items():
            with self.subTest(payout=payout):
                casino, writer = new_casino("3", "100", "0", games={"roulette": FakeGame(payout)})
                casino.menu()
                self.assertIn("ПІДСУМОК СЕСІЇ", writer.text)
                self.assertIn(expected, writer.text)

    def test_exit_message_shows_balance(self):
        casino, writer = new_casino("0")
        casino.menu()
        self.assertIn("Дякуємо за гру! Ваш підсумковий баланс: $500", writer.text)


class TestMenuSimulation(unittest.TestCase):
    def test_simulation_is_delegated_to_game_21(self):
        game = FakeCardGame()
        casino, _ = new_casino("4", "10", "7", "0", games={"21": game})
        casino.menu()
        self.assertEqual(game.simulations, [(10, 7)])

    def test_invalid_rounds_default_to_ten(self):
        game = FakeCardGame()
        casino, writer = new_casino("4", "10", "abc", "0", games={"21": game})
        casino.menu()
        self.assertEqual(game.simulations, [(10, 10)])
        self.assertIn("Некоректна кількість ігор", writer.text)


class TestMenuEdgeCases(unittest.TestCase):
    def test_missing_game_is_reported_and_balance_untouched(self):
        casino, writer = new_casino("1", "0", games={})
        casino.menu()
        self.assertIn("недоступна", writer.text)
        self.assertEqual(casino.balance, 500)

    def test_missing_simulation_is_reported(self):
        casino, writer = new_casino("4", "0", games={})
        casino.menu()
        self.assertIn("Симуляція недоступна", writer.text)

    def test_zero_balance_blocks_play(self):
        game = FakeGame()
        casino, writer = new_casino("3", "0", games={"roulette": game}, balance=0)
        casino.menu()
        self.assertIn("Немає коштів", writer.text)
        self.assertEqual(game.bets, [])

    def test_unknown_menu_option(self):
        casino, writer = new_casino("9", "0")
        casino.menu()
        self.assertIn("Невідомий пункт меню", writer.text)

    def test_exhausted_input_ends_session_gracefully(self):
        casino, writer = new_casino()
        casino.menu()
        self.assertIn("Файл введення закінчився", writer.text)
        self.assertIn("ПІДСУМОК СЕСІЇ", writer.text)


if __name__ == "__main__":
    unittest.main()
