# Supported Python runtime

## Scope

The README now declares Python 3.9 or newer as the supported runtime and notes
that the project uses only the Python standard library. A focused regression
test keeps the documented baseline aligned with the interpreter running the
suite. No generator code or output contract changed.

## Verification

- `python3 --version`: Python 3.9.6.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`: 37 tests passed.
- Read-only syntax compilation of `main.py`, `batch.py`, `test_main.py`, and
  `test_batch.py`: passed.
- A temporary default CLI run produced the expected Rule 30 text rows and no
  opt-in metrics, SVG, or metadata sidecars.
- `git diff --check`: passed.

## Classification

`INCREMENTAL / EMPIRICAL`. This formalizes the tested runtime documentation;
it makes no claim about cellular-automaton behavior or scientific novelty.
