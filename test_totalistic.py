import contextlib
import io
import json
import unittest

import totalistic


class TotalisticCliTests(unittest.TestCase):
    def test_cli_defaults_to_100_steps(self):
        args = totalistic.build_parser().parse_args(["--rule", "0"])
        self.assertEqual(args.steps, 100)

    def test_cli_prints_history_as_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            totalistic.main(["--rule", "63", "--steps", "4"])

        expected = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
        ]
        self.assertEqual(
            json.loads(output.getvalue()),
            expected,
        )
        self.assertEqual(output.getvalue(), json.dumps(expected) + "\n")

    def test_cli_metadata_wraps_history_with_reproduction_contract(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            totalistic.main(["--rule", "63", "--steps", "4", "--metadata"])

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["radius"], 2)
        self.assertEqual(payload["rule"], 63)
        self.assertEqual(payload["rule_bits"], "111111")
        self.assertEqual(payload["steps"], 4)
        self.assertEqual(payload["width"], 8)
        self.assertEqual(payload["seed_index"], 4)
        self.assertEqual(payload["boundary"], "fixed-dead")
        self.assertEqual(payload["rule_encoding"], "bit n = output for n active cells")
        self.assertEqual(
            payload["history"],
            [
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
            ],
        )

    def test_cli_rejects_invalid_totalistic_inputs_without_stdout(self):
        for arguments in (["--rule", "64"], ["--rule", "0", "--steps", "0"]):
            with self.subTest(arguments=arguments):
                output = io.StringIO()
                error = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit) as raised:
                        totalistic.main(arguments)
                self.assertEqual(raised.exception.code, 2)
                self.assertEqual(output.getvalue(), "")
                self.assertIn("error:", error.getvalue())


if __name__ == "__main__":
    unittest.main()
