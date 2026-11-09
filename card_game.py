from typing import Callable

from deck import Deck
from game import Game
from hand import Hand


class CardGame(Game):
    """Клас карткових ігор, що успадковує Game."""

    def __init__(self, name: str, is_blackjack: bool = True,
                 deck_factory: Callable[[bool], Deck] = Deck):
        super().__init__(name)
        self._is_bj = is_blackjack
        self._deck_factory = deck_factory

    def get_rules(self) -> str:
        if self._is_bj:
            return "Правила Блекджек: 52 карти. Ціль — набрати суму ближче до 21."
        return "Правила 21: 36 карт. Ціль — набрати 21 або більше ніж у дилера."

    def play(self, casino, bet: int) -> int:
        io = casino.io
        deck = self._deck_factory(self._is_bj)
        p_hand = Hand("Гравець")
        d_hand = Hand("Дилер")

        io.say(f"\n--- {self.name} ---")
        io.say(self.get_rules())

        for _ in range(2):
            p_hand.add_card(deck.draw())
            d_hand.add_card(deck.draw())

        io.say(f"\nВаші карти: {[c.show() for c in p_hand.cards]} | Сума: {p_hand.get_score()}")

        if p_hand.get_score() <= 21 and io.ask("1 - Добрати, 0 - Паси: ").strip() == "1":
            p_hand.add_card(deck.draw())
            io.say(f"Ваші карти: {[c.show() for c in p_hand.cards]} | Сума: {p_hand.get_score()}")

        p_score = p_hand.get_score()
        d_score = d_hand.get_score()
        io.say(f"Карти дилера: {[c.show() for c in d_hand.cards]} | Сума: {d_score}")

        if p_score <= 21 and (d_score > 21 or p_score > d_score):
            win_amount = bet * 2
            io.say(f"🎉 Виграш! +${win_amount}")
            return win_amount
        elif p_score <= 21 and p_score == d_score:
            io.say("🤝 Нічия! Ставка повертається.")
            return bet
        else:
            io.say("❌ Програш.")
            return 0

    def simulate(self, casino, bet: int, rounds: int) -> None:
        io = casino.io
        wins, losses, draws = 0, 0, 0
        start_balance = casino.balance
        played_rounds = 0

        io.say(f"\n... Запуск симуляції {rounds} ігор у '{self.name}' зі ставкою ${bet} ...")

        for _ in range(rounds):
            if casino.balance < bet:
                io.say("💸 Баланс вичерпано під час симуляції!")
                break

            played_rounds += 1
            casino.deduct_balance(bet)
            deck = self._deck_factory(self._is_bj)
            p_score = deck.draw().get_value() + deck.draw().get_value()
            d_score = deck.draw().get_value() + deck.draw().get_value()

            if p_score <= 21 and (d_score > 21 or p_score > d_score):
                wins += 1
                casino.add_balance(bet * 2)
            elif p_score <= 21 and p_score == d_score:
                draws += 1
                casino.add_balance(bet)
            else:
                losses += 1

        profit = casino.balance - start_balance
        io.say("\n" + "=" * 30)
        io.say("📊 РЕЗУЛЬТАТИ СИМУЛЯЦІЇ 📊")
        io.say(f"Зіграно раундів: {played_rounds}")
        io.say(f"Перемог: {wins} | Поразок: {losses} | Нічій: {draws}")
        io.say(f"Підсумок: {'+' if profit >= 0 else ''}${profit}")
        io.say(f"Новий баланс: ${casino.balance}")
        io.say("=" * 30)
