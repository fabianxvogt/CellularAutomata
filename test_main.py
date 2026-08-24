import contextlib
import io
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from main import (
    active_cell_density,
    center_column,
    render_metadata,
    render_metrics,
    render_svg,
    run,
    totalistic_metadata,
    totalistic_history,
    totalistic_step,
    validate_rule,
    validate_totalistic_rule,
)
import main


class RunValidationTests(unittest.TestCase):
    def test_readme_declares_supported_python_runtime(self):
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        self.assertIn("Requires Python 3.9 or newer", readme)
        self.assertGreaterEqual(sys.version_info[:2], (3, 9))

    def test_active_cell_density_measures_rendered_rows(self):
        self.assertEqual(active_cell_density(["  ■ ", " ■■ "]), 3 / 8)
        self.assertEqual(active_cell_density(["000", " ■ "]), 1 / 6)

    def test_active_cell_density_rejects_empty_or_malformed_rows(self):
        with self.assertRaises(ValueError):
            active_cell_density([])
        with self.assertRaises(ValueError):
            active_cell_density(["■", "  "])
        with self.assertRaises(ValueError):
            active_cell_density(["x"])
        with self.assertRaises(TypeError):
            active_cell_density([["■"]])

    def test_center_column_tracks_the_generator_seed_column(self):
        self.assertEqual(center_column(["  ■ ", " ■■ ", " ■ ■"]), "110")
        self.assertEqual(center_column(["■  ", " ■ ", "  ■"]), "010")

    def test_center_column_rejects_empty_or_malformed_rows(self):
        with self.assertRaises(ValueError):
            center_column([])
        with self.assertRaises(ValueError):
            center_column(["■", "  "])
        with self.assertRaises(TypeError):
            center_column([["■"]])

    def test_render_metrics_reports_density_and_activity(self):
        self.assertEqual(
            render_metrics(["  ■ ", " ■■ "]),
            {
                "activity_over_time": [0.0, 0.25],
                "density_over_time": [0.25, 0.5],
                "mean_activity": 0.125,
                "mean_density": 0.375,
                "steps": 2,
                "width": 4,
            },
        )

    def test_render_metadata_describes_run_and_requested_outputs(self):
        self.assertEqual(
            render_metadata(
                30,
                ["  ■ ", " ■■ "],
                metrics=True,
                svg=True,
                cell_size=2,
                metadata=True,
            ),
            {
                "schema_version": 1,
                "rule": 30,
                "steps": 2,
                "width": 4,
                "options": {"cell_size": 2, "metrics": True, "svg": True},
                "outputs": {
                    "text": "rule_30_output.txt",
                    "metrics": "rule_30_metrics.json",
                    "svg": "rule_30_output.svg",
                    "metadata": "rule_30_metadata.json",
                },
            },
        )

    def test_render_svg_contains_background_and_active_cells(self):
        svg = render_svg(["  ■ ", " ■■ "], cell_size=2)
        root = ET.fromstring(svg)
        self.assertIn('viewBox="0 0 8 4"', svg)
        self.assertIn('width="8" height="4"', svg)
        self.assertEqual(svg.count('fill="#111827"'), 3)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertTrue(svg.endswith("</svg>\n"))

    def test_render_svg_rejects_invalid_cell_size(self):
        for cell_size in (0, -1, True, "2"):
            with self.subTest(cell_size=cell_size):
                with self.assertRaises((TypeError, ValueError)):
                    render_svg(["■"], cell_size=cell_size)

    def test_run_rejects_invalid_cell_size_before_creating_output(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "not-created"
            for cell_size in (0, True, "2"):
                with self.subTest(cell_size=cell_size):
                    with self.assertRaises((TypeError, ValueError)):
                        run(30, 2, output_dir=output, cell_size=cell_size)
                    self.assertFalse(output.exists())

    def test_active_cell_density_can_be_computed_from_run_output(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                run(30, 2, output_dir=output)
            lines = (Path(output) / "rule_30_output.txt").read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(active_cell_density(lines), 3 / 8)

    def test_cli_writes_to_requested_directory(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                main.main(["--rule", "30", "--steps", "2", "--output-dir", output])
            self.assertEqual(
                (Path(output) / "rule_30_output.txt").read_text(encoding="utf-8").splitlines(),
                ["  ■ ", " ■■ "],
            )
            self.assertFalse((Path(output) / "rule_30_metrics.json").exists())
            self.assertFalse((Path(output) / "rule_30_metadata.json").exists())

    def test_cli_metadata_writes_opt_in_sidecar_without_changing_text_output(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                main.main(
                    [
                        "--rule",
                        "30",
                        "--steps",
                        "2",
                        "--output-dir",
                        output,
                        "--metadata",
                    ]
                )
            self.assertEqual(
                (Path(output) / "rule_30_output.txt").read_text(encoding="utf-8").splitlines(),
                ["  ■ ", " ■■ "],
            )
            metadata = json.loads(
                (Path(output) / "rule_30_metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["rule"], 30)
            self.assertEqual(metadata["steps"], 2)
            self.assertEqual(metadata["width"], 4)
            self.assertEqual(
                metadata["options"],
                {"cell_size": 4, "metrics": False, "svg": False},
            )
            self.assertEqual(metadata["outputs"]["text"], "rule_30_output.txt")
            self.assertIsNone(metadata["outputs"]["metrics"])
            self.assertIsNone(metadata["outputs"]["svg"])
            self.assertEqual(metadata["outputs"]["metadata"], "rule_30_metadata.json")

    def test_cli_metrics_writes_structured_json_sidecar(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                main.main(
                    [
                        "--rule",
                        "30",
                        "--steps",
                        "2",
                        "--output-dir",
                        output,
                        "--metrics",
                    ]
                )
            metrics = json.loads(
                (Path(output) / "rule_30_metrics.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metrics["density_over_time"], [0.25, 0.5])
            self.assertEqual(metrics["activity_over_time"], [0.0, 0.25])
            self.assertEqual(metrics["steps"], 2)
            self.assertEqual(metrics["width"], 4)

    def test_cli_svg_writes_sidecar_without_changing_text_output(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                main.main(
                    [
                        "--rule",
                        "30",
                        "--steps",
                        "2",
                        "--output-dir",
                        output,
                        "--svg",
                        "--cell-size",
                        "2",
                    ]
                )
            self.assertEqual(
                (Path(output) / "rule_30_output.txt").read_text(encoding="utf-8").splitlines(),
                ["  ■ ", " ■■ "],
            )
            svg = (Path(output) / "rule_30_output.svg").read_text(encoding="utf-8")
            self.assertIn('viewBox="0 0 8 4"', svg)
            self.assertFalse((Path(output) / "rule_30_metrics.json").exists())

    def test_cli_rejects_cell_size_without_svg(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main.main(["--rule", "30", "--steps", "1", "--cell-size", "2"])

    def test_accepts_rule_boundaries_and_positive_steps(self):
        with tempfile.TemporaryDirectory() as output:
            with patch("main.Path", lambda value: Path(output) if value == "output" else Path(value)):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(set(run(0, 1)), {"000", "001", "010", "011", "100", "101", "110", "111"})
                    run(255, 1)

    def test_rule_validator_accepts_complete_elementary_rule_table(self):
        self.assertEqual(
            [validate_rule(rule) for rule in range(256)],
            list(range(256)),
        )

    def test_totalistic_rule_validator_accepts_complete_six_bit_table(self):
        self.assertEqual(
            [validate_totalistic_rule(rule) for rule in range(64)],
            list(range(64)),
        )

    def test_totalistic_step_exhaustively_maps_rules_and_neighborhoods(self):
        for rule in range(64):
            for neighborhood in range(32):
                state = [
                    (neighborhood >> bit) & 1
                    for bit in range(4, -1, -1)
                ]
                with self.subTest(rule=rule, neighborhood=neighborhood):
                    result = totalistic_step(state, rule)
                    self.assertEqual(result[:2], [0, 0])
                    self.assertEqual(result[2], (rule >> sum(state)) & 1)
                    self.assertEqual(result[3:], [0, 0])

    def test_totalistic_history_uses_seed_and_fixed_radius_two_boundaries(self):
        self.assertEqual(
            totalistic_history(63, 4),
            [
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
            ],
        )

    def test_totalistic_metadata_describes_history_generation_contract(self):
        payload = totalistic_metadata(63, 4)
        self.assertEqual(
            {key: payload[key] for key in payload if key != "history"},
            {
                "schema_version": 1,
                "radius": 2,
                "rule": 63,
                "rule_encoding": "bit n = output for n active cells",
                "steps": 4,
                "width": 8,
                "seed_index": 4,
                "boundary": "fixed-dead",
            },
        )
        self.assertEqual(payload["history"], totalistic_history(63, 4))

    def test_totalistic_helpers_reject_invalid_inputs(self):
        for rule in (-1, 64, True, "30"):
            with self.subTest(rule=rule):
                with self.assertRaises((TypeError, ValueError)):
                    validate_totalistic_rule(rule)
        for state in ([], [0, 2], [True], "010"):
            with self.subTest(state=state):
                with self.assertRaises((TypeError, ValueError)):
                    totalistic_step(state, 0)
        for no_steps in (0, -1, True, 1.5):
            with self.subTest(no_steps=no_steps):
                with self.assertRaises((TypeError, ValueError)):
                    totalistic_history(0, no_steps)

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
