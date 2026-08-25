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

The activity calculation uses the logical cell state rather than raw marker
characters: both a space and the accepted legacy `0` marker mean inactive.
This keeps activity aligned with density and SVG rendering for older text
outputs that still contain zero padding.

## Evidence

- `python3 -m unittest -v`: 18 tests passed.
- Focused tests cover exact density/activity values, JSON sidecar parsing, and
  the default no-sidecar behavior, including equivalence of legacy `0` and
  space inactive markers.
- The implementation uses only the Python standard library and the existing
  atomic-write helper.

## Current use

This is an instrumentation contract, not evidence about cellular-automata
complexity or randomness. The current batch runner forwards `metrics=True` (or
the CLI's `--metrics` flag) to each requested rule, producing the same JSON
sidecar contract per output.
