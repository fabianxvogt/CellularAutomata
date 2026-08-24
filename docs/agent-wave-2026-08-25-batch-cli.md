# CellularAutomata batch wave — 2026-08-25

## Change

Added `batch.py`, a dependency-free CLI and `run_batch()` helper for rendering
an ordered, unique comma-separated rule list. The complete list and step count
are validated before the first output directory or file is created. Each rule
keeps the existing `rule_<n>_output.txt` naming contract; `--metrics` forwards
the existing optional JSON sidecar behavior to every rule.

## Evidence

- `python3 -m pytest -q` — full suite passed, including five focused batch tests.
- Temporary batch run for Rules 30 and 90 at two steps wrote two text outputs and
  two metrics sidecars, and returned results in the requested order.
- Invalid batch `[30, 256]` left its nested output directory absent.
- `python3 -m py_compile batch.py test_batch.py` — passed.
- `git diff --check` — clean for this wave.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This adds orchestration convenience and input
validation; it makes no claim about cellular-automaton complexity or randomness.
