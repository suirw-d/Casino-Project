import random

from game import Game


class RouletteGame(Game):
    """Клас Рулетки, що успадковує Game."""

    def __init__(self):
        super().__init__("Рулетка")
        self._colors = {"Червоне": [1, 3, 5], "Чорне": [2, 4, 6]}
        self._last_num = 0

    def get_rules(self) -> str:
        return (
            "\n--- 📜 ПРАВИЛА РУЛЕТКИ ---\n"
            "• Вибір 1 (Червоне): числа 1, 3, 5. Виграш x2.\n"
            "• Вибір 2 (Чорне):   числа 2, 4, 6. Виграш x2.\n"
            "• Вибір 3 (Зеро):     число 0.       Виграш x14."
        )

    def play(self, casino, bet: int) -> int:
        io = casino.io
        io.say(self.get_rules())
        choice = io.ask("Оберіть ставку (1 - Червоне, 2 - Чорне, 3 - Зеро): ").strip()

        self._last_num = random.randint(0, 6)
        if self._last_num == 0:
            color = "Зеро (0)"
        elif self._last_num in self._colors["Червоне"]:
            color = "Червоне"
        else:
            color = "Чорне"

        io.say(f"\n🎰 Кулька зупинилася на: {self._last_num} ({color})!")

        if choice == "3" and self._last_num == 0:
            io.say("💡 Вгадали Зеро! Множник x14.")
            return bet * 14
        elif choice == "1" and self._last_num in self._colors["Червоне"]:
            io.say("💡 Вгадали Червоне! Множник x2.")
            return bet * 2
        elif choice == "2" and self._last_num in self._colors["Чорне"]:
            io.say("💡 Вгадали Чорне! Множник x2.")
            return bet * 2

        io.say("💡 Колір або число не співпали.")
        return 0
