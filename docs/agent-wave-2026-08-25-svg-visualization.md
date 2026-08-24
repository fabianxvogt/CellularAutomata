# Dependency-free SVG visualization

## Scope

Added an opt-in SVG sidecar for single and batch elementary cellular-automaton
runs. The `--svg` flag writes `rule_<n>_output.svg`; `--cell-size` controls
the square size of each cell and defaults to 4. Existing text output, stdout,
and optional JSON metrics remain unchanged unless the new flag is requested.

## Evidence

- `render_svg()` uses only the Python standard library and the existing text
  representation; active cells are rendered as crisp-edged SVG rectangles.
- Focused tests cover geometry, invalid cell sizes, single-run sidecars, and
  batch sidecars.
- The SVG output is written through the existing atomic-write path.

## Verification

- `python3 -m unittest discover -v`: 31 tests passed.
- `python3 -m py_compile main.py batch.py test_main.py test_batch.py`: syntax check.
- `git diff --check`: whitespace check.
- A direct CLI probe with `--metrics --svg --cell-size 3` produced text, JSON,
  and SVG sidecars; `xml.etree.ElementTree` parsed the SVG successfully.

## Classification

`INCREMENTAL / EMPIRICAL`. This is a tested rendering path, not a claim about
the scientific behavior or novelty of any cellular automaton rule.
