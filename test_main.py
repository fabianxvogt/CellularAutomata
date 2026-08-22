import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import run


class RunValidationTests(unittest.TestCase):
    def test_accepts_rule_boundaries_and_positive_steps(self):
        with tempfile.TemporaryDirectory() as output:
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(set(run(0, 1)), {"000", "001", "010", "011", "100", "101", "110", "111"})
                    run(255, 1)

    def test_rejects_rule_outside_eight_bit_range(self):
        for rule in (-1, 256):
            with self.subTest(rule=rule):
                with self.assertRaises(ValueError):
                    run(rule, 1)

    def test_rejects_non_integer_rule(self):
        for rule in ("30", True, False):
            with self.subTest(rule=rule):
                with self.assertRaises(TypeError):
                    run(rule, 1)

    def test_rejects_boolean_steps(self):
        for no_steps in (True, False):
            with self.subTest(no_steps=no_steps):
                with self.assertRaises(TypeError):
                    run(30, no_steps)

    def test_invalid_input_does_not_create_or_change_output(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output) / "rule_30_output.txt"
            output_path.write_text("existing output\n", encoding="utf-8")
            before = {path.relative_to(output): path.read_bytes() for path in Path(output).iterdir()}
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                for rule, no_steps in ((True, 1), (256, 1), (30, False), (30, 0)):
                    with self.subTest(rule=rule, no_steps=no_steps):
                        with self.assertRaises((TypeError, ValueError)):
                            run(rule, no_steps)
            after = {path.relative_to(output): path.read_bytes() for path in Path(output).iterdir()}
            self.assertEqual(after, before)

    def test_rejects_non_positive_steps(self):
        for no_steps in (0, -1):
            with self.subTest(no_steps=no_steps):
                with self.assertRaises(ValueError):
                    run(30, no_steps)

    def test_rejects_non_integer_steps(self):
        with self.assertRaises(TypeError):
            run(30, 1.5)

    def test_successful_output_has_expected_content_and_no_temporary_file(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output) / "rule_30_output.txt"
            output_path.write_text("old output\n", encoding="utf-8")
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                with contextlib.redirect_stdout(io.StringIO()):
                    run(30, 2)
            self.assertEqual(output_path.read_text(encoding="utf-8").splitlines(), ["  ■ ", " ■■ "])
            self.assertEqual(list(Path(output).glob(".rule_30_output.txt.*.tmp")), [])

    def test_keyword_output_dir_writes_to_temporary_directory(self):
        with tempfile.TemporaryDirectory() as output:
            target = Path(output) / "nested"
            with contextlib.redirect_stdout(io.StringIO()):
                run(30, 2, output_dir=target)
            self.assertEqual(
                (target / "rule_30_output.txt").read_text(encoding="utf-8").splitlines(),
                ["  ■ ", " ■■ "],
            )

    def test_output_dir_is_keyword_only(self):
        with self.assertRaises(TypeError):
            run(30, 1, tempfile.mkdtemp())

    def test_output_failure_preserves_existing_file_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output) / "rule_30_output.txt"
            original = "existing output\n"
            output_path.write_text(original, encoding="utf-8")
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                with patch("main.os.replace", side_effect=OSError("replace failed")):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(OSError):
                            run(30, 2)
            self.assertEqual(output_path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(output).glob(".rule_30_output.txt.*.tmp")), [])

    def test_write_failure_preserves_existing_file_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output) / "rule_30_output.txt"
            original = "existing output\n"
            output_path.write_text(original, encoding="utf-8")
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                with patch("main.os.fsync", side_effect=OSError("write failed")):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(OSError):
                            run(30, 2)
            self.assertEqual(output_path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(output).glob(".rule_30_output.txt.*.tmp")), [])
            self.assertEqual(list(Path(output).iterdir()), [output_path])


if __name__ == "__main__":
    unittest.main()
