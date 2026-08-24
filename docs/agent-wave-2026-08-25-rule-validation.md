# Elementary-rule validation wave — 2026-08-25

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is an API-contract improvement, not evidence
about cellular-automaton complexity, randomness, or novelty.

## Change

`main.py` now exposes one dependency-free `validate_rule()` helper for the
elementary Wolfram rule domain `0–255`. Both `run()` and the batch runner use
that helper, so the single-rule and batch APIs share the same type and range
contract. Tests exercise every accepted rule number through the direct helper
and the comma-separated batch parser.

## Evidence

- `python3 -m unittest -v` — full suite passed.
- Focused tests cover all 256 valid rule values and reject values outside the
  eight-bit range through the existing single and batch validation cases.
- `python3 -m py_compile main.py batch.py test_main.py test_batch.py` — passed.
- `git diff --check` — clean.
- Tests use temporary directories; no generated repository output was changed.

## Limits and next check

The table proves accepted-input coverage only. It does not establish that every
rule produces a distinct or scientifically interesting pattern. A later family
cross-link can connect this input contract to the GameOfLife and Rule 30
companion projects without changing the renderer.
