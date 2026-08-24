# Project-family cross-links

Classification: `INCREMENTAL` / `EMPIRICAL`.

The project README now links to the public GameOfLife and Rule 30 repositories,
making the three related cellular-automata projects discoverable as one family.
This is a documentation-only change; runtime behavior, generated output, and
dependencies are unchanged.

## Family scope

The shared comparison surface is deliberately descriptive: binary cells, local
deterministic updates, seeded finite histories, and inspectable per-generation
states. The projects cover different dimensions and questions:

- `CellularAutomata`: 1D elementary rules and the tested radius-2 totalistic
  history core, including its JSON CLI.
- `GameOfLife`: 2D finite-board pattern evolution and classic creature
  behavior.
- `rule30`: 1D Rule 30 center-column and finite predictive-state research.

This is not a common simulator or a rule-equivalence claim. It does not imply a
shared randomness result, periodicity result, or cross-project scientific
comparison.

Verification:

- Confirmed both Markdown destinations use the expected public GitHub URLs.
- Confirmed the family descriptions match the current bounded APIs and their
  explicit limits.
- `git diff --check` passed.
