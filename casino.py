import logging
from typing import Dict

from file_io import GameIO, InputExhaustedError
from game import Game

logger = logging.getLogger(__name__)


class Casino:
    """Головний клас управління Казино."""

    def __init__(self, game_io: GameIO, games: Dict[str, Game],
                 name: str = "ДОДЕПОВКА", initial_balance: int = 500):
        self._io = game_io
        self._name = name
        self._balance = initial_balance
        self._start_balance = initial_balance
        self._history = []
        self._games = games
        logger.info("Казино '%s' створено. Початковий баланс: $%s. Ігор: %s",
                    self._name, self._balance, list(self._games))

    @property
    def balance(self) -> int:
        return self._balance

    @property
    def io(self) -> GameIO:
        return self._io

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
            bet = int(self._io.ask(f"Введіть ставку (доступно ${self._balance}): "))
            if bet <= 0 or bet > self._balance:
                self._io.say("Некоректна сума! Встановлено мінімальну ставку $10.")
                logger.warning("Некоректна ставка %s (баланс $%s). Використано мінімальну.",
                               bet, self._balance)
                return min(10, self._balance)
            logger.debug("Гравець зробив ставку $%s", bet)
            return bet
        except ValueError:
            self._io.say("Помилка вводу! Встановлено мінімальну ставку $10.")
            logger.warning("Нечисловий ввід ставки. Використано мінімальну.")
            return min(10, self._balance)

    def menu(self) -> None:
        """Запускає меню; сесія завершується вибором '0' або коли закінчився файл введення."""
        logger.info("Меню казино запущено")
        try:
            self._run_menu()
        except InputExhaustedError:
            self._io.say("\n⚠️ Файл введення закінчився — сесію завершено автоматично.")
            logger.warning("Сесію завершено: вичерпано файл введення")
        self._print_summary()

    def _run_menu(self) -> None:
        while True:
            self._io.say(f"\n=== КАЗИНО '{self._name}' | Баланс: ${self._balance} ===")
            self._io.say("1. Зіграти в 21\n2. Зіграти в Блекджек\n3. Рулетка\n4. Симуляція ігор\n0. Вихід")

            choice = self._io.ask("Вибір: ").strip()
            logger.debug("Вибір у меню: %r", choice)

            if choice in ("1", "2", "3"):
                if self._balance <= 0:
                    self._io.say("💸 Немає коштів для гри!")
                    logger.warning("Спроба зіграти з нульовим балансом")
                    continue

                game_key = "21" if choice == "1" else ("bj" if choice == "2" else "roulette")
                if game_key not in self._games:
                    self._io.say("⚠️ Ця гра недоступна.")
                    logger.warning("Гру '%s' не передано в казино", game_key)
                    continue

                bet = self.get_bet()
                self.deduct_balance(bet)

                logger.info("Початок гри '%s', ставка $%s", game_key, bet)
                try:
                    payout = self._games[game_key].play(self, bet)
                except Exception:
                    logger.exception("Помилка під час гри '%s'", game_key)
                    raise
                self.add_balance(payout)
                self._history.append((game_key, bet, payout))
                logger.info("Гру '%s' завершено. Виплата: $%s, баланс: $%s",
                            game_key, payout, self._balance)

            elif choice == "4":
                if self._balance <= 0:
                    self._io.say("💸 Немає коштів для симуляції!")
                    logger.warning("Спроба симуляції з нульовим балансом")
                    continue

                game = self._games.get("21")
                if game is None:
                    self._io.say("⚠️ Симуляція недоступна.")
                    logger.warning("Гру '21' не передано в казино")
                    continue

                bet = self.get_bet()
                try:
                    rounds = int(self._io.ask("Скільки ігор симулювати?: "))
                except ValueError:
                    rounds = 10
                    self._io.say("Некоректна кількість ігор. Використано значення за замовчуванням: 10.")
                    logger.warning("Некоректна кількість ігор. Використано значення за замовчуванням: %s", rounds)
                logger.info("Запуск симуляції: ставка $%s, ігор: %s", bet, rounds)
                try:
                    game.simulate(self, bet, rounds)
                except Exception:
                    logger.exception("Помилка під час симуляції")
                    raise
                logger.info("Симуляцію завершено. Баланс: $%s", self._balance)

            elif choice == "0":
                self._io.say(f"Дякуємо за гру! Ваш підсумковий баланс: ${self._balance}")
                logger.info("Вихід з казино. Підсумковий баланс: $%s", self._balance)
                break

            else:
                self._io.say(f"Невідомий пункт меню: {choice!r}")
                logger.debug("Невідомий пункт меню: %r", choice)

    def _print_summary(self) -> None:
        """Записує у файл виводу статистику всієї сесії."""
        wins = sum(1 for _, bet, payout in self._history if payout > bet)
        draws = sum(1 for _, bet, payout in self._history if payout == bet)
        losses = len(self._history) - wins - draws
        profit = self._balance - self._start_balance

        self._io.say("\n" + "=" * 30)
        self._io.say("📋 ПІДСУМОК СЕСІЇ 📋")
        self._io.say(f"Зіграно ігор (без симуляцій): {len(self._history)}")
        self._io.say(f"Перемог: {wins} | Поразок: {losses} | Нічій: {draws}")
        self._io.say(f"Початковий баланс: ${self._start_balance}")
        self._io.say(f"Підсумковий баланс: ${self._balance} ({'+' if profit >= 0 else '-'}${abs(profit)})")
        self._io.say("=" * 30)
        logger.info("Підсумок сесії записано: ігор %s, перемог %s, поразок %s, нічій %s",
                    len(self._history), wins, losses, draws)
