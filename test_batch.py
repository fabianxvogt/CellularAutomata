import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import batch


class BatchRunnerTests(unittest.TestCase):
    def test_parse_rules_preserves_order_and_whitespace(self):
        self.assertEqual(batch.parse_rules(" 30, 90,110 "), [30, 90, 110])

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


if __name__ == "__main__":
    unittest.main()
