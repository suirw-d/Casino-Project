import argparse
import io
import logging
import os
import random
import sys

from card_game import CardGame
from casino import Casino
from deck import Deck
from file_io import ConsoleInput, ConsoleWriter, FileInput, FileWriter, GameIO
from roulette_game import RouletteGame

# Папка з main.py: файли шукаємо поруч із програмою, а не в папці, з якої запущено термінал
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Налаштування UTF-8 для консолі Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename=os.path.join(BASE_DIR, "casino.log"),
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

DEFAULT_INPUT = os.path.join(BASE_DIR, "input.txt")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "output.txt")
DEFAULT_NAME = "ДОДЕПОВКА"
DEFAULT_BALANCE = 500


def read_int_setting(settings: dict, key: str, default: int) -> int:
    """Повертає числове налаштування з файлу або значення за замовчуванням."""
    value = settings.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Некоректне значення @%s=%r, використано %s", key, value, default)
        return default


def build_games(rng: random.Random) -> dict:
    """Створює ігри казино. Єдиний генератор випадкових чисел передається в усі ігри."""
    def deck_factory(is_blackjack: bool) -> Deck:
        return Deck(is_blackjack, rng)

    return {
        "21": CardGame("Гра 21", is_blackjack=False, deck_factory=deck_factory),
        "bj": CardGame("Блекджек", is_blackjack=True, deck_factory=deck_factory),
        "roulette": RouletteGame(rng),
    }


def run(input_path: str, output_path: str) -> int:
    """Запускає казино: відповіді беруться з input_path, результати пишуться в output_path."""
    try:
        reader = FileInput(input_path)
    except FileNotFoundError:
        logger.error("Файл введення '%s' не знайдено", input_path)
        print(f"Помилка: файл введення '{input_path}' не знайдено.")
        return 1

    settings = reader.settings
    if "seed" in settings:
        rng = random.Random(settings["seed"])
        logger.info("Встановлено seed=%s", settings["seed"])
    else:
        rng = random.Random()

    with FileWriter(output_path) as writer:
        casino = Casino(
            GameIO(reader, writer),
            build_games(rng),
            name=settings.get("name", DEFAULT_NAME),
            initial_balance=read_int_setting(settings, "balance", DEFAULT_BALANCE),
        )
        casino.menu()

    print(f"Готово! Результати гри збережено у файлі '{output_path}'.")
    return 0


def run_console() -> int:
    """Інтерактивний режим: гравець відповідає в консолі, як у початковій версії гри."""
    logger.info("Запуск у консольному режимі")
    casino = Casino(
        GameIO(ConsoleInput(), ConsoleWriter(), echo=False),
        build_games(random.Random()),
        name=DEFAULT_NAME,
        initial_balance=DEFAULT_BALANCE,
    )
    casino.menu()
    return 0


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Казино: введення з файлу, результати у файл.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="файл з відповідями гравця")
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT, help="файл для результатів гри")
    parser.add_argument("--console", action="store_true",
                        help="грати вручну в консолі (файли введення/виводу не потрібні)")
    return parser.parse_args(argv)


if __name__ == "__main__":
    # Використання: python main.py [input.txt] [output.txt]   або   python main.py --console
    args = parse_args(sys.argv[1:])
    sys.exit(run_console() if args.console else run(args.input, args.output))