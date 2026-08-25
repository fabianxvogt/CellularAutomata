# Stale-sidecar cleanup error aggregation — 2026-08-25

## Finding

`_remove_unrequested_sidecars()` already attempted every known stale sidecar,
but it re-raised only the first `OSError`. If two stale entries failed, the
later failure was lost even though the file remained protected. A directory at
the metrics sidecar path reproduced this together with an injected metadata
unlink failure: the directory raised `IsADirectoryError`, while the metadata
failure was not reported.

## Change

Single cleanup failures retain their original exception type and message. When
multiple known sidecars fail, the helper now raises a private `OSError`
subclass containing each `(path, error)` pair and a deterministic summary. The
helper still attempts every known sidecar, removes no directories recursively,
and leaves each failed or protected entry in place. Optional-write failures
continue to preserve their primary write error because cleanup errors remain
secondary in that path.

## Evidence

- Failure injection: a protected `rule_30_metrics.json` directory plus a
  separate metadata unlink failure produced one aggregated error containing
  both sidecar paths and both underlying exceptions.
- The committed text output was emitted unchanged; the protected directory,
  sentinel file, and metadata file remained byte-for-byte intact.
- `python3 -m unittest discover -s . -p 'test*.py' -q` — full suite passed.
- `python3 -m py_compile main.py batch.py totalistic.py 1d.py` — compilation
  passed.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This improves diagnostics for bounded known-sidecar
cleanup without changing sidecar schemas, cleanup scope, or multi-file
transaction semantics.
