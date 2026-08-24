# Radius-2 totalistic core — 2026-08-25

## Scope

Added dependency-free `validate_totalistic_rule()`, `totalistic_step()`, and
`totalistic_history()` helpers for binary radius-2 totalistic rules. A rule has
six bits: bit `n` determines the next state for a five-cell neighborhood with
`n` active cells. The helpers use fixed-dead boundaries and do not write files.

The existing `run()`/`run_batch()` signatures, default text output, sidecars,
and return values are unchanged. Full radius-2 non-totalistic tables remain
deferred because their rule domain has `2^32` entries and would require a larger
rule/output contract.

## Evidence

- Tests cover every one of the 64 totalistic rules against all 32 possible
  five-cell neighborhoods (`2,048` rule/neighborhood cases).
- Seeded history and invalid-input behavior are covered separately.
- Full suite, syntax checks, and whitespace checks pass.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a bounded experiment-harness extension; it
makes no claim about complexity, randomness, or novelty.
