# CellularAutomata stdout commit boundary — 2026-08-25

## Finding

The elementary renderer prints each generated row while it is still preparing
requested output. If SVG or JSON rendering/serialization then fails, the
filesystem correctly remains unchanged, but callers have already received
rows that look like a successful result.

## Change

`run()` now emits its rendered rows only after the text replacement and every
requested sidecar replacement complete. A successful run retains the existing
row-for-row stdout contract. A failed requested-output preparation does not
emit a partial success-looking stream. A later stale-sidecar cleanup error is
reported after the committed primary rows are emitted, because that cleanup
does not invalidate the requested primary output.

## Evidence

- Baseline failure injection: the second requested JSON serialization raised
  `metadata serialization failed`; stdout contained the two rendered rows even
  though the output directory was never created.
- Regression test: the same failure now leaves stdout empty while preserving
  the existing assertion that no output or temporary file is created.
- `python3 -m unittest discover -s . -p 'test*.py' -q` — 66 tests passed.
- `python3 -m py_compile main.py batch.py totalistic.py 1d.py` — compilation
  passed.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is an output-integrity boundary for the
dependency-free renderer. It does not make the multi-file sidecar replacement
sequence transactional and makes no claims about recovery from broken stdout
or filesystem failures.
