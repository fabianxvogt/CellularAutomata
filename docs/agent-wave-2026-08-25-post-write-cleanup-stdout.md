# Post-write cleanup/stdout boundary — 2026-08-25

## Finding

When a rerun had already replaced its text output and finished all requested
sidecar replacements, `_remove_unrequested_sidecars()` could still fail while
removing a stale optional sidecar. `run()` raised that cleanup error before
printing any rows. The new primary output was therefore present on disk while
the caller received an empty stdout stream, even though the requested output
itself had committed successfully.

## Change

`run()` now retains the first stale-sidecar cleanup error, emits the committed
primary rows, and then re-raises that same error. Requested-output failures
still raise before stdout, and the cleanup error remains visible to callers.
The stale sidecar is intentionally left in place when its injected unlink
fails; this change does not broaden cleanup scope or make sidecar replacement
transactional.

## Evidence

- Failure injection: unlinking `rule_30_output.svg` raised `svg cleanup failed`
  after a three-row text replacement. Before the fix, stdout was empty while
  the text file had three rows and the stale SVG remained.
- Regression coverage now verifies that the emitted rows are byte-for-byte
  equal to the committed text file, the cleanup error is preserved, the stale
  SVG remains protected, and a different stale metadata sidecar is still
  removed.
- `python3 -m unittest discover -s . -p 'test*.py' -q` — full suite passed.
- `python3 -m py_compile main.py batch.py totalistic.py 1d.py` — compilation
  passed.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This aligns the primary stdout stream with a
successfully committed text/requested-sidecar set while preserving explicit
cleanup failure reporting. It does not claim multi-file transactionality or
recovery from a broken stdout stream.
