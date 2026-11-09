import unittest

from file_io import ConsoleInput, ConsoleWriter, FileWriter, GameIO
from interfaces import IInputSource, IOutputSink


class ListInput(IInputSource):
    """Тестова реалізація інтерфейсу: відповіді беруться зі списку."""

    def __init__(self, answers):
        self._answers = list(answers)

    def read(self, prompt: str = "") -> str:
        return self._answers.pop(0)


class ListOutput(IOutputSink):
    """Тестова реалізація інтерфейсу: рядки складаються у список."""

    def __init__(self):
        self.lines = []

    def write(self, text: str = "") -> None:
        self.lines.append(text)


class TestInterfaces(unittest.TestCase):
    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            IInputSource()
        with self.assertRaises(TypeError):
            IOutputSink()

    def test_class_without_method_cannot_be_created(self):
        class BrokenInput(IInputSource):
            pass  # метод read() не реалізовано

        with self.assertRaises(TypeError):
            BrokenInput()

    def test_project_classes_implement_interfaces(self):
        self.assertIsInstance(ConsoleInput(), IInputSource)
        self.assertIsInstance(ConsoleWriter(), IOutputSink)
        self.assertTrue(issubclass(FileWriter, IOutputSink))

    def test_game_io_works_with_any_implementation(self):
        out = ListOutput()
        game_io = GameIO(ListInput(["42"]), out)
        self.assertEqual(game_io.ask("Ставка: "), "42")
        self.assertEqual(out.lines, ["Ставка: 42"])

    def test_game_io_rejects_object_without_interface(self):
        with self.assertRaises(TypeError):
            GameIO("не джерело", ListOutput())


if __name__ == "__main__":
    unittest.main()
