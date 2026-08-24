# Structured metrics probe — 2026-08-25

## Classification

**INCREMENTAL** — a small, dependency-free CLI/API improvement; no claim of
scientific novelty.

## Change

`main.py` now exposes `render_metrics(lines)` and an opt-in `--metrics` flag.
The flag writes `rule_<n>_metrics.json` beside the text output with
`density_over_time`, `activity_over_time`, their means, row count, and width.
Activity is the fraction of cells changed from the preceding generation, with
generation zero defined as `0.0`. Existing text output and the `run()` return
value are unchanged when metrics are not requested.

## Evidence

- `python3 -m unittest -v`: 18 tests passed.
- Focused tests cover exact density/activity values, JSON sidecar parsing, and
  the default no-sidecar behavior.
- The implementation uses only the Python standard library and the existing
  atomic-write helper.

## Limits and next check

This is an instrumentation contract, not evidence about cellular-automata
complexity or randomness. A later batch interface can consume the same JSON
schema after its rule/step bounds are specified.
