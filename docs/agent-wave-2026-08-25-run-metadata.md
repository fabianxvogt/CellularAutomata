# Run metadata sidecar

## Scope

Single-rule and batch rendering now accept the opt-in `metadata` API keyword
and CLI `--metadata` flag. Each requested run writes a dependency-free JSON
sidecar describing the rule, rendered width and step count, enabled metrics/SVG
options, the metadata flag itself, and the filenames for its text and optional
sidecars. Existing output files and default CLI behavior are unchanged when the
option is omitted. This keeps the existing schema version and fields intact
while making the already-present `outputs.metadata` filename self-describing.

## Contract audit

The metadata sidecar previously named `rule_<n>_metadata.json` in `outputs` but
did not report `metadata: true` in `options`. The envelope now records all three
sidecar flags (`metrics`, `svg`, and `metadata`); the totalistic history
metadata round-trip was checked across all 64 rules at horizons 1, 2, 4, and 8
with no mismatches.

## Verification

- `python3 -m unittest discover -v`: passed with the metadata regression tests.
- `python3 -m py_compile main.py batch.py test_main.py test_batch.py`: passed.
- `git diff --check`: passed.
- A temporary CLI probe verified JSON parsing for single and batch metadata
  sidecars and confirmed the existing text output remained unchanged.

## Classification

`INCREMENTAL / EMPIRICAL`. This is runtime metadata plumbing only; it makes no
claim about cellular-automaton behavior, randomness, or scientific novelty.
