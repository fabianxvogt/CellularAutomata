# CellularAutomata batch wave — 2026-08-25

## Change

Added `batch.py`, a dependency-free CLI for rendering an ordered, unique
comma-separated rule list and a `run_batch(rules, no_steps=100, *,
output_dir=None, metrics=False, svg=False, cell_size=4, metadata=False)` helper
for the corresponding ordered iterable. The complete list and step count are
validated before the first output directory or file is created. Each rule keeps
the existing `rule_<n>_output.txt` naming contract; the optional metrics, SVG,
and run-metadata sidecars are forwarded to every rule.

The Python APIs now require `metrics`, `svg`, and `metadata` to be actual
booleans, matching the CLI flag contract. Batch mode rejects non-boolean
sidecar options before the first output directory or file is created.

## Evidence

- `python3 -m pytest -q` — full suite passed: 53 tests, including the new
  single and batch option-validation regressions.
- Temporary batch run for Rules 30 and 90 at two steps wrote two text outputs and
  two metrics sidecars, and returned results in the requested order.
- Invalid batch `[30, 256]` left its nested output directory absent.
- Invalid sidecar option values such as `svg="false"` leave the target output
  directory absent for both single and batch APIs.
- `python3 -m py_compile main.py batch.py totalistic.py test_main.py
  test_batch.py test_totalistic.py` — passed.
- `git diff --check` — clean for this wave.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This adds orchestration convenience and input
validation; it makes no claim about cellular-automaton complexity or randomness.
