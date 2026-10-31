from card_game import CardGame
from roulette_game import RouletteGame


class Casino:
    """Головний клас управління Казино."""

    def __init__(self, name: str = "ДОДЕПОВКА", initial_balance: int = 500):
        self._name = name
        self._balance = initial_balance
        self._games = {
            "21": CardGame("Гра 21", is_blackjack=False),
            "bj": CardGame("Блекджек", is_blackjack=True),
            "roulette": RouletteGame(),
        }

    @property
    def balance(self) -> int:
        return self._balance

    def add_balance(self, amount: int) -> None:
        if amount > 0:
            self._balance += amount

    def deduct_balance(self, amount: int) -> None:
        if 0 < amount <= self._balance:
            self._balance -= amount

    def get_bet(self) -> int:
        try:
            bet = int(input(f"Введіть ставку (доступно ${self._balance}): "))
            if bet <= 0 or bet > self._balance:
                print("Некоректна сума! Встановлено мінімальну ставку $10.")
                return min(10, self._balance)
            return bet
        except ValueError:
            print("Помилка вводу! Встановлено мінімальну ставку $10.")
            return min(10, self._balance)

    def menu(self) -> None:
        while True:
            print(f"\n=== КАЗИНО '{self._name}' | Баланс: ${self._balance} ===")
            print("1. Зіграти в 21\n2. Зіграти в Блекджек\n3. Рулетка\n4. Симуляція ігор\n0. Вихід")

            choice = input("Вибір: ").strip()

            if choice in ("1", "2", "3"):
                if self._balance <= 0:
                    print("💸 Немає коштів для гри!")
                    continue

                bet = self.get_bet()
                self.deduct_balance(bet)

                game_key = "21" if choice == "1" else ("bj" if choice == "2" else "roulette")
                payout = self._games[game_key].play(self, bet)
                self.add_balance(payout)

            elif choice == "4":
                if self._balance <= 0:
                    print("💸 Немає коштів для симуляції!")
                    continue
                bet = self.get_bet()
                try:
                    rounds = int(input("Скільки ігор симулювати?: "))
                except ValueError:
                    rounds = 10
                self._games["21"].simulate(self, bet, rounds)

            elif choice == "0":
                print(f"Дякуємо за гру! Ваш підсумковий баланс: ${self._balance}")
                break