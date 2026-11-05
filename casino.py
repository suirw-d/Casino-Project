import logging

from card_game import CardGame
from roulette_game import RouletteGame

logger = logging.getLogger(__name__)


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
        logger.info("Казино '%s' створено. Початковий баланс: $%s. Ігор: %s",
                    self._name, self._balance, list(self._games))

    @property
    def balance(self) -> int:
        return self._balance

    def add_balance(self, amount: int) -> None:
        if amount > 0:
            self._balance += amount
            logger.info("Баланс поповнено на $%s. Новий баланс: $%s", amount, self._balance)
        else:
            logger.debug("add_balance проігноровано: amount=%s", amount)

    def deduct_balance(self, amount: int) -> None:
        if 0 < amount <= self._balance:
            self._balance -= amount
            logger.info("З балансу списано $%s. Новий баланс: $%s", amount, self._balance)
        else:
            logger.warning("Списання відхилено: amount=%s, баланс=$%s", amount, self._balance)

    def get_bet(self) -> int:
        try:
            bet = int(input(f"Введіть ставку (доступно ${self._balance}): "))
            if bet <= 0 or bet > self._balance:
                print("Некоректна сума! Встановлено мінімальну ставку $10.")
                logger.warning("Некоректна ставка %s (баланс $%s). Використано мінімальну.",
                               bet, self._balance)
                return min(10, self._balance)
            logger.debug("Гравець зробив ставку $%s", bet)
            return bet
        except ValueError:
            print("Помилка вводу! Встановлено мінімальну ставку $10.")
            logger.warning("Нечисловий ввід ставки. Використано мінімальну.")
            return min(10, self._balance)

    def menu(self) -> None:
        logger.info("Меню казино запущено")
        while True:
            print(f"\n=== КАЗИНО '{self._name}' | Баланс: ${self._balance} ===")
            print("1. Зіграти в 21\n2. Зіграти в Блекджек\n3. Рулетка\n4. Симуляція ігор\n0. Вихід")

            choice = input("Вибір: ").strip()
            logger.debug("Вибір у меню: %r", choice)

            if choice in ("1", "2", "3"):
                if self._balance <= 0:
                    print("💸 Немає коштів для гри!")
                    logger.warning("Спроба зіграти з нульовим балансом")
                    continue

                bet = self.get_bet()
                self.deduct_balance(bet)

                game_key = "21" if choice == "1" else ("bj" if choice == "2" else "roulette")
                logger.info("Початок гри '%s', ставка $%s", game_key, bet)
                try:
                    payout = self._games[game_key].play(self, bet)
                except Exception:
                    logger.exception("Помилка під час гри '%s'", game_key)
                    raise
                self.add_balance(payout)
                logger.info("Гру '%s' завершено. Виплата: $%s, баланс: $%s",
                            game_key, payout, self._balance)

            elif choice == "4":
                if self._balance <= 0:
                    print("💸 Немає коштів для симуляції!")
                    logger.warning("Спроба симуляції з нульовим балансом")
                    continue
                bet = self.get_bet()
                try:
                    rounds = int(input("Скільки ігор симулювати?: "))
                except ValueError:
                    rounds = 10
                    logger.warning("Некоректна кількість ігор. Використано значення за замовчуванням: %s", rounds)
                logger.info("Запуск симуляції: ставка $%s, ігор: %s", bet, rounds)
                try:
                    self._games["21"].simulate(self, bet, rounds)
                except Exception:
                    logger.exception("Помилка під час симуляції")
                    raise
                logger.info("Симуляцію завершено. Баланс: $%s", self._balance)

            elif choice == "0":
                print(f"Дякуємо за гру! Ваш підсумковий баланс: ${self._balance}")
                logger.info("Вихід з казино. Підсумковий баланс: $%s", self._balance)
                break

            else:
                logger.debug("Невідомий пункт меню: %r", choice)