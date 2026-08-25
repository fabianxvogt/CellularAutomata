# Radius-2 totalistic CLI — 2026-08-25

## Scope

Added `totalistic.py`, a dependency-free command-line entry point for the
existing `totalistic_history(rule, no_steps=100)` API. It requires a totalistic
`--rule` from `0–63`, accepts a positive `--steps` value (default `100`), and
prints the binary history as JSON to standard output. It does not create files.

The existing `main.py` elementary-automaton CLI, `run()` behavior, default
outputs, and raw `totalistic_history()` behavior are unchanged. The current
radius-2 API also includes the later opt-in metadata helpers documented in
[the metadata note](agent-wave-2026-08-25-totalistic-metadata.md).

## Evidence

- The CLI test verifies JSON output for a known radius-2 rule and seeded history.
- Invalid rule and step values are rejected through the core validators without
  writing to standard output.
- The full test suite, syntax checks, and whitespace checks pass.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a bounded usability wrapper around the
existing core; it makes no claim about complexity, randomness, or novelty.
