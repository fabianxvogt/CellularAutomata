# CellularAutomata metrics wave — 2026-08-25

## Change

Added `active_cell_density(lines)` to `main.py`. It is a pure helper for rows
read from the existing text output and computes:

```text
number of `■` markers / total rendered cells
```

Spaces and the legacy `0` padding marker count as inactive cells. Rows must be
non-empty, equally sized strings using only the existing output markers. The
helper does not read or write files, and `run()` still returns the same
neighborhood-count dictionary.

## Interpretation

This is a descriptive occupancy statistic for the selected finite run: it
summarizes how many rendered cells are active across all generations included
in `lines`. It depends on the run width, number of steps, initial condition,
boundary behavior, and rendering format. It is not a complexity measure, a
randomness measure, or evidence about Rule 30's computational complexity.

## Evidence

- `python3 -m pytest -q` — full test suite passed, including helper validation
  and computation from a real temporary output file.
- Temporary Rule 30 CLI run: `python3 main.py --rule 30 --steps 12` wrote 12
  rows to a temporary directory; the helper measured the resulting occupancy
  as `86 / 288 = 0.2986111111111111`.
- The existing two-step Rule 30 text rows remain `  ■ ` and ` ■■ `, and their
  density is `3 / 8 = 0.375`.
- `git diff --check` — clean.

## Classification

`INCREMENTAL`, `EMPIRICAL`. The metric is a small descriptive aid only; no
complexity result or novelty claim is made.
