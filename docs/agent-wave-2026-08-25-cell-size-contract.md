# Cell-size validation contract

## Scope

The single-rule and batch Python APIs now validate `cell_size` before creating
the requested output directory, even when SVG output is disabled. This keeps
the optional SVG parameter explicit and prevents invalid values from being
silently ignored by callers that assemble options programmatically.

## Evidence

- `run()` and `run_batch()` share the existing positive-integer validator.
- Focused tests cover zero, boolean, and string values and assert that no
  output directory is created after rejection.
- Valid SVG output and the default text-only path remain unchanged.

## Verification

- `python3 -m unittest discover -v`: 33 tests passed.
- `python3 -m py_compile main.py batch.py test_main.py test_batch.py`: passed.
- `git diff --check`: passed.
- A temporary `batch.py --rules 30,90 --steps 3 --metrics --svg
  --cell-size 3` probe produced six valid text/JSON/SVG files; JSON and XML
  parsed successfully and the CLI emitted one summary line.

## Classification

`INCREMENTAL / EMPIRICAL`. This is an input-contract hardening change; it
makes no claim about the behavior or novelty of any cellular-automaton rule.
