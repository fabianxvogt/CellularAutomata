# Run metadata sidecar

## Scope

Single-rule and batch rendering now accept the opt-in `metadata` API keyword
and CLI `--metadata` flag. Each requested run writes a dependency-free JSON
sidecar describing the rule, rendered width and step count, enabled metrics/SVG
options, and the filenames for its text and optional sidecars. Existing output
files and default CLI behavior are unchanged when the option is omitted.

## Verification

- `python3 -m unittest discover -v`: passed with the metadata regression tests.
- `python3 -m py_compile main.py batch.py test_main.py test_batch.py`: passed.
- `git diff --check`: passed.
- A temporary CLI probe verified JSON parsing for single and batch metadata
  sidecars and confirmed the existing text output remained unchanged.

## Classification

`INCREMENTAL / EMPIRICAL`. This is runtime metadata plumbing only; it makes no
claim about cellular-automaton behavior, randomness, or scientific novelty.
