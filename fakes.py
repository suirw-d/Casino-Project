"""Допоміжні заглушки для юніт-тестів (самі тести тут не містяться)."""
from card import Card
from file_io import GameIO, InputExhaustedError
from game import Game
from interfaces import IInputSource, IOutputSink


class ListReader(IInputSource):
    """Віддає заздалегідь підготовлені відповіді гравця по черзі."""

    def __init__(self, answers):
        self._answers = list(answers)

    def read(self, prompt: str = "") -> str:
        if not self._answers:
            raise InputExhaustedError("Відповіді закінчилися")
        return self._answers.pop(0)


class ListWriter(IOutputSink):
    """Збирає все, що гра «виводить», у список рядків."""

    def __init__(self):
        self.lines = []

    def write(self, text: str = "") -> None:
        self.lines.append(text)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def make_io(*answers):
    """Повертає (GameIO, writer): відповіді беруться зі списку, вивід збирається в writer.lines."""
    writer = ListWriter()
    return GameIO(ListReader(answers), writer, echo=False), writer


class StackedDeck:
    """Колода з наперед заданим порядком карт: draw() віддає їх по черзі."""

    def __init__(self, ranks, suit="♠"):
        self._cards = [Card(rank, suit) for rank in ranks]

    def draw(self):
        return self._cards.pop(0) if self._cards else None


def stacked_factory(*ranks):
    """Фабрика колод для CardGame(deck_factory=...): кожен виклик дає нову колоду з тим самим порядком."""
    calls = []

    def factory(is_blackjack=True):
        calls.append(is_blackjack)
        return StackedDeck(ranks)

    factory.calls = calls
    return factory


class FakeRng:
    """Замість random.Random: randint завжди повертає задане число."""

    def __init__(self, value):
        self._value = value
        self.calls = []

    def randint(self, a, b):
        self.calls.append((a, b))
        return self._value


class FakeGame(Game):
    """Гра-заглушка: запам'ятовує ставки й завжди виплачує задану суму."""

    def __init__(self, payout=0, name="fake"):
        super().__init__(name)
        self.payout = payout
        self.bets = []

    def play(self, casino, bet):
        self.bets.append(bet)
        return self.payout

    def get_rules(self):
        return "rules"
