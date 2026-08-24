# Radius-2 totalistic CLI — 2026-08-25

## Scope

Added `totalistic.py`, a dependency-free command-line entry point for the
existing `totalistic_history()` API. It requires a six-bit `--rule`, accepts a
positive `--steps` value (default `100`), and prints the binary history as JSON
to standard output. It does not create files.

The existing `main.py` elementary-automaton CLI, `run()` behavior, default
outputs, and radius-2 API are unchanged.

## Evidence

- The CLI test verifies JSON output for a known radius-2 rule and seeded history.
- Invalid rule and step values are rejected through the core validators without
  writing to standard output.
- The full test suite, syntax checks, and whitespace checks pass.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a bounded usability wrapper around the
existing core; it makes no claim about complexity, randomness, or novelty.
