# Casino Project

A simple casino simulator that allows users to play different casino games and simulate game outcomes.

## Features

- **Blackjack** – Play the classic card game against the dealer.
- **21** – Play a card game where the goal is to reach 21 points without exceeding it.
- **Game Simulation** – Simulate casino games and observe their outcomes.
- **Roulette** – Place bets and spin the roulette wheel.

## Запуск (введення/виведення через файли)

Програма не читає з консолі й не виводить у консоль: усі відповіді гравця беруться з файлу, а весь хід гри записується в інший файл.

```
python main.py [input.txt] [output.txt]
```

Якщо імена файлів не вказані, використовуються `input.txt` та `output.txt`.

### Формат `input.txt`

- Рядки, що починаються з `@`, — налаштування: `@name=...`, `@balance=...`, `@seed=...` (seed робить гру відтворюваною).
- Решта непорожніх рядків — відповіді гравця, програма читає їх по черзі у порядку запитань (вибір у меню, ставка, «добрати/пас» тощо).
- Усе після `#` — коментар.
- Якщо файл закінчився раніше за гру, сесія завершується автоматично, а в `output.txt` записується підсумок.

Приклад — у файлі `input.txt` у корені проєкту.

### Тести

```
python -m unittest
```

## About

This project was created as an university assignment as well as just to practice programming skills and to explore how to use github in a team.
