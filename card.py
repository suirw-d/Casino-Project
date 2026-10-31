class Card:
    """Клас Карти з інкапсульованими атрибутами."""

    def __init__(self, rank: str, suit: str):
        self._rank = rank
        self._suit = suit

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def suit(self) -> str:
        return self._suit

    def get_value(self) -> int:
        values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, 
            "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11
        }
        return values.get(self._rank, 0)

    def show(self) -> str:
        return f"{self._rank}{self._suit}"