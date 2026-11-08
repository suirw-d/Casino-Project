import logging

logger = logging.getLogger(__name__)


class InputExhaustedError(Exception):
    """Вхідний файл закінчився раніше, ніж програма отримала всі відповіді."""


class FileInput:
    """Читає налаштування та відповіді гравця з текстового файлу.

    Формат файлу:
      * рядки, що починаються з '@', — налаштування (@name=..., @balance=..., @seed=...);
      * решта непорожніх рядків — відповіді гравця, їх програма читає по черзі;
      * усе після символу '#' — коментар, він ігнорується.
    """

    def __init__(self, path: str = "input.txt"):
        self._path = path
        self._answers = []
        self._settings = {}
        self._pos = 0
        self._load()

    @property
    def settings(self) -> dict:
        return dict(self._settings)

    @property
    def remaining(self) -> int:
        return len(self._answers) - self._pos

    def _load(self) -> None:
        # utf-8-sig, щоб файл, збережений у Блокноті Windows (з BOM), читався коректно
        with open(self._path, encoding="utf-8-sig") as file:
            for number, raw in enumerate(file, start=1):
                line = raw.split("#", 1)[0].strip()
                if not line:
                    continue
                if line.startswith("@"):
                    self._parse_setting(line[1:], number)
                else:
                    self._answers.append(line)
        logger.info("Файл '%s' прочитано: відповідей %s, налаштувань %s",
                    self._path, len(self._answers), len(self._settings))

    def _parse_setting(self, text: str, line_number: int) -> None:
        key, separator, value = text.partition("=")
        if not separator or not key.strip():
            logger.warning("Рядок %s: некоректне налаштування %r пропущено", line_number, text)
            return
        self._settings[key.strip().lower()] = value.strip()

    def read(self, prompt: str = "") -> str:
        """Повертає наступну відповідь із файлу (prompt потрібен лише консольному режиму)."""
        if self._pos >= len(self._answers):
            logger.warning("Вхідний файл '%s' вичерпано", self._path)
            raise InputExhaustedError(f"Вхідний файл '{self._path}' закінчився.")
        value = self._answers[self._pos]
        self._pos += 1
        logger.debug("Прочитано відповідь #%s: %r", self._pos, value)
        return value


class FileWriter:
    """Записує результати гри у текстовий файл."""

    def __init__(self, path: str = "output.txt"):
        self._path = path
        self._file = open(path, "w", encoding="utf-8")
        logger.info("Файл виводу '%s' відкрито", path)

    def write(self, text: str = "") -> None:
        self._file.write(text + "\n")
        self._file.flush()

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()
            logger.info("Файл виводу '%s' закрито", self._path)

    def __enter__(self) -> "FileWriter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class ConsoleInput:
    """Читає відповіді гравця прямо з консолі (режим --console)."""

    def read(self, prompt: str = "") -> str:
        try:
            return input(prompt).strip()
        except EOFError:
            raise InputExhaustedError("Введення з консолі завершено.") from None


class ConsoleWriter:
    """Виводить текст у консоль (режим --console)."""

    def write(self, text: str = "") -> None:
        print(text, flush=True)


class GameIO:
    """Єдина точка введення/виведення для всіх ігор (замість input() та print()).

    echo=True — записувати у вивід і запитання з відповіддю (файловий режим);
    echo=False — не дублювати їх (консольний режим: запитання і так видно в консолі).
    """

    def __init__(self, reader, writer, echo: bool = True):
        self._reader = reader
        self._writer = writer
        self._echo = echo

    def say(self, text: str = "") -> None:
        """Виводить рядок (у файл або в консоль)."""
        self._writer.write(text)

    def ask(self, prompt: str) -> str:
        """Бере відповідь із джерела введення; у файловому режимі записує «питання — відповідь»."""
        try:
            answer = self._reader.read(prompt)
        except InputExhaustedError:
            if self._echo:
                self._writer.write(f"{prompt}<немає даних>")
            raise
        if self._echo:
            self._writer.write(f"{prompt}{answer}")
        return answer