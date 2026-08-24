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

        self.assertEqual(
            json.loads(output.getvalue()),
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
