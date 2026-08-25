# Stale-sidecar cleanup exception surface — 2026-08-25

## Audit

The single and aggregated stale-sidecar cleanup paths were exercised with a
directory at a known sidecar path and injected `OSError` failures. The
observable exception contracts are intentionally different by cardinality:

| Case | Concrete type | Cause | Message |
| --- | --- | --- | --- |
| One ordinary failure | the original `OSError` subtype | none; the raised object is the underlying failure | the original message |
| One unsafe path/message | `_LineSafeSidecarCleanupError` | the original cleanup error | one escaped, single-line report |
| Multiple failures | `_SidecarCleanupError` | the first underlying cleanup error | one escaped, single-line report containing every failure |

Wrapped errors have no ambient `__context__`; aggregate failures remain
available through the bounded `failures` tuple. No runtime inconsistency was
reproduced, so the implementation was unchanged.

## Consistency evidence

- In all three cases, captured stdout was byte-for-byte equal to the committed
  text output.
- A failed stale-sidecar removal left that entry and its contents protected.
- Other known stale sidecars were still attempted and removed.
- The primary text output and requested sidecars were already committed before
  the cleanup error was raised.

Regression assertions cover concrete type, cause, context, message shape,
stdout/file equality, and stale-file protection in `test_main.py`.

## Verification

- `python3 -m unittest discover -s . -p 'test*.py' -q` — passed.
- `python3 -m py_compile main.py batch.py totalistic.py 1d.py` — passed.
- `git diff --check` — passed.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a contract audit and regression-locking
change only; it does not alter sidecar schemas, cleanup scope, or exception
semantics.
