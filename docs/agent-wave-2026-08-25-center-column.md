# Center-column extraction

## Scope

Added the pure `center_column(lines)` helper for extracting the active-cell
state of each rendered generation as a binary string. For the generator's
even-width rows it selects `width // 2`, the column used for the initial active
cell. It reads existing text rows only; default stdout, text output, sidecars,
and the `run()` return value are unchanged.

## Evidence

- Focused tests cover even-width generator rows, odd-width rows, and malformed
  input validation.
- The full test suite and syntax checks passed for this change.
- `git diff --check` passed.

## Classification

`INCREMENTAL / EMPIRICAL`. This is an experiment-harness convenience for
center-column inspection; it is not a randomness result or novelty claim.
