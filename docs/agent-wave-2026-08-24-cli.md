# CellularAutomata CLI wave — 2026-08-24

## Change

Added a dependency-free `argparse` entry point to `main.py` with `--rule`,
`--steps`, and `--output-dir`. It delegates to the existing validated `run()`
function, so invalid inputs still fail before output mutation.

## Evidence

- `python3 -m pytest -q` — 13 tests passed.
- `python3 main.py --rule 30 --steps 2 --output-dir <temporary directory>` —
  produced the expected two-line Rule 30 output.
- `python3 main.py --help` — lists all three options.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, EMPIRICAL evidence limited to the CLI parser and the existing
text-output path. No image rendering or performance claim is made.

## Next falsifiable check

Add a table-driven CLI test for rule values 0 and 255 and assert that the
generated output contains only the expected all-dead or all-active transitions.
