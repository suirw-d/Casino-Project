from abc import ABC, abstractmethod


class Game(ABC):
    """Абстрактний базовий клас для всіх ігор у казино."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def play(self, casino, bet: int) -> int:
        """Абстрактний метод проведення гри."""

    @abstractmethod
    def get_rules(self) -> str:
        """Абстрактний метод для отримання правил гри."""