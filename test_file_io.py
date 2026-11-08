import os
import tempfile
import unittest

from file_io import FileInput, FileWriter, GameIO, InputExhaustedError


class FileIOTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def path(self, name: str) -> str:
        return os.path.join(self._tmp.name, name)

    def make_input(self, text: str) -> FileInput:
        path = self.path("input.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return FileInput(path)


class TestFileInput(FileIOTestCase):
    def test_answers_are_read_in_order(self):
        reader = self.make_input("1\n50\n0\n")
        self.assertEqual([reader.read(), reader.read(), reader.read()], ["1", "50", "0"])

    def test_comments_and_blank_lines_are_ignored(self):
        reader = self.make_input("# коментар\n\n7  # в кінці рядка\n")
        self.assertEqual(reader.read(), "7")
        self.assertEqual(reader.remaining, 0)

    def test_settings_are_parsed(self):
        reader = self.make_input("@Balance=1000\n@name = Тест\n5\n")
        self.assertEqual(reader.settings, {"balance": "1000", "name": "Тест"})
        self.assertEqual(reader.remaining, 1)

    def test_broken_setting_is_skipped(self):
        reader = self.make_input("@balance\n@=5\n")
        self.assertEqual(reader.settings, {})

    def test_exhausted_input_raises(self):
        reader = self.make_input("1\n")
        reader.read()
        with self.assertRaises(InputExhaustedError):
            reader.read()

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            FileInput(self.path("немає.txt"))

    def test_utf8_bom_is_supported(self):
        path = self.path("bom.txt")
        with open(path, "w", encoding="utf-8-sig") as file:
            file.write("@balance=300\n1\n")
        self.assertEqual(FileInput(path).settings, {"balance": "300"})


class TestGameIO(FileIOTestCase):
    def test_say_and_ask_are_written_to_file(self):
        out_path = self.path("output.txt")
        with FileWriter(out_path) as writer:
            game_io = GameIO(self.make_input("42\n"), writer)
            game_io.say("Привіт")
            self.assertEqual(game_io.ask("Ставка: "), "42")
        with open(out_path, encoding="utf-8") as file:
            self.assertEqual(file.read(), "Привіт\nСтавка: 42\n")

    def test_ask_on_empty_input_marks_output_and_raises(self):
        out_path = self.path("output.txt")
        with FileWriter(out_path) as writer:
            game_io = GameIO(self.make_input(""), writer)
            with self.assertRaises(InputExhaustedError):
                game_io.ask("Вибір: ")
        with open(out_path, encoding="utf-8") as file:
            self.assertEqual(file.read(), "Вибір: <немає даних>\n")


if __name__ == "__main__":
    unittest.main()
