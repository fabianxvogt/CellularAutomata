import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import batch


class BatchRunnerTests(unittest.TestCase):
    def test_parse_rules_preserves_order_and_whitespace(self):
        self.assertEqual(batch.parse_rules(" 30, 90,110 "), [30, 90, 110])

    def test_parse_rules_accepts_complete_elementary_rule_table(self):
        specification = ",".join(str(rule) for rule in range(256))
        self.assertEqual(batch.parse_rules(specification), list(range(256)))

    def test_parse_rules_rejects_empty_invalid_and_duplicate_entries(self):
        for spec in ("", "30,,90", "30,nope", "30,30", "-1,30", "30,256"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    batch.parse_rules(spec)

    def test_run_batch_validates_before_creating_output(self):
        with tempfile.TemporaryDirectory() as output:
            target = Path(output) / "not-created"
            with self.assertRaises(ValueError):
                batch.run_batch([30, 256], 2, output_dir=target)
            self.assertFalse(target.exists())

    def test_run_batch_writes_each_rule_and_optional_metrics(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                results = batch.run_batch(
                    [30, 90], 2, output_dir=output, metrics=True
                )
            self.assertEqual(list(results), [30, 90])
            for rule in (30, 90):
                self.assertTrue((Path(output) / f"rule_{rule}_output.txt").is_file())
                self.assertTrue((Path(output) / f"rule_{rule}_metrics.json").is_file())

    def test_run_batch_writes_opt_in_metadata_sidecars(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                batch.run_batch([30, 90], 2, output_dir=output, metadata=True)
            for rule in (30, 90):
                metadata = json.loads(
                    (Path(output) / f"rule_{rule}_metadata.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(metadata["rule"], rule)
                self.assertEqual(metadata["steps"], 2)
                self.assertFalse(metadata["options"]["metrics"])
                self.assertFalse(metadata["options"]["svg"])
                self.assertTrue(metadata["options"]["metadata"])
                self.assertIsNone(metadata["outputs"]["metrics"])
                self.assertIsNone(metadata["outputs"]["svg"])
                self.assertEqual(
                    metadata["outputs"]["metadata"],
                    f"rule_{rule}_metadata.json",
                )

    def test_run_batch_writes_svg_sidecars_when_requested(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                batch.run_batch([30, 90], 2, output_dir=output, svg=True)
            for rule in (30, 90):
                svg_path = Path(output) / f"rule_{rule}_output.svg"
                self.assertTrue(svg_path.is_file())
                self.assertIn("<svg ", svg_path.read_text(encoding="utf-8"))

    def test_successful_batch_rerun_removes_unrequested_sidecars(self):
        with tempfile.TemporaryDirectory() as output:
            with contextlib.redirect_stdout(io.StringIO()):
                batch.run_batch(
                    [30, 90],
                    2,
                    output_dir=output,
                    metrics=True,
                    svg=True,
                    metadata=True,
                )
                batch.run_batch([30, 90], 3, output_dir=output)

            output_dir = Path(output)
            self.assertEqual(
                sorted(path.name for path in output_dir.iterdir()),
                ["rule_30_output.txt", "rule_90_output.txt"],
            )

    def test_run_batch_rejects_invalid_cell_size_before_first_output(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "not-created"
            for cell_size in (0, True, "2"):
                with self.subTest(cell_size=cell_size):
                    with self.assertRaises((TypeError, ValueError)):
                        batch.run_batch([30, 90], 2, output_dir=output, cell_size=cell_size)
                    self.assertFalse(output.exists())

    def test_run_batch_rejects_non_boolean_sidecar_options_before_first_output(self):
        with tempfile.TemporaryDirectory() as parent:
            output = Path(parent) / "not-created"
            invalid_options = (("metrics", 1), ("svg", "false"), ("metadata", None))
            for option, value in invalid_options:
                with self.subTest(option=option, value=value):
                    with self.assertRaises(TypeError):
                        batch.run_batch(
                            [30, 90], 2, output_dir=output, **{option: value}
                        )
                    self.assertFalse(output.exists())

    def test_cli_reports_one_summary_for_a_batch(self):
        with tempfile.TemporaryDirectory() as output:
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                batch.main(
                    ["--rules", "30,90", "--steps", "2", "--output-dir", output]
                )
            self.assertEqual(
                captured.getvalue(), "generated 2 rule outputs (2 steps each)\n"
            )

    def test_cli_rejects_cell_size_without_svg(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                batch.main(["--rules", "30", "--steps", "1", "--cell-size", "2"])


if __name__ == "__main__":
    unittest.main()
