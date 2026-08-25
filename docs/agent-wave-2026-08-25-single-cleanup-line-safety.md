# Single stale-sidecar cleanup line safety — 2026-08-25

## Finding

The aggregated stale-sidecar error report escaped unusual paths and messages,
but a single cleanup failure was re-raised unchanged. An injected newline in
the cleanup message therefore remained visible in `str(run(...))`, and a rule
value with a newline could also create an unusual known sidecar name.

## Change

Ordinary single cleanup failures still re-raise the original exception object,
preserving its existing type and message. Only when the sidecar name or
exception text needs escaping does `run()` raise a private `OSError` subclass
with a deterministic one-line report; the original cleanup exception remains
available as `__cause__`. The stale entry remains protected, and stdout remains
the committed text output before the cleanup error is raised.

## Evidence

- A newline-producing integer-subclass rule and an injected
  `cleanup failed\nwith details` error produced a one-line report containing
  escaped sidecar and message text.
- The original cleanup error was preserved as the wrapped exception's cause;
  the stale metrics sidecar remained in place.
- `python3 -m unittest discover -s . -p 'test*.py' -q` — full suite passed.
- `python3 -m py_compile main.py batch.py totalistic.py 1d.py` — compilation
  passed.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This narrows a single known-sidecar diagnostic
boundary without changing sidecar schemas, cleanup scope, or ordinary single
failure behavior.
