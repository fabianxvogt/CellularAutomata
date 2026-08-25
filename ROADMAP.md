# CellularAutomata Roadmap

Small tool that generates 1D elementary cellular automata: `run(rule, steps)` renders a
rule (e.g. Rule 30 for 100 steps) and writes text output, with configurable output
directory, atomic writes, and tests. Companion to `toy-projects/GameOfLife` and the
Rule 30 open-problem project.

## Now

1. [x] Add a CLI entry point (`python3 main.py --rule 30 --steps 100`) so the tool is
   usable without writing Python.
2. [x] Render output as a dependency-free SVG sidecar alongside the text files;
   visual patterns are the point of CA experiments.
3. [x] Run the test suite after the atomic-write, output-dir, and visualization changes.
4. [x] Pin the Python version in the README when the supported runtime is formalized.

## Next

- [x] Support all 256 elementary rules explicitly with a rule-number validation table test.
- [x] Add basic metrics per run (density over time, activity) written next to the output.
- [x] Add dependency-free batch mode for an ordered set of rules at N steps.
- [x] Ignore known root-generated artifacts (`test.json`, `output/`) without touching local files.
- [x] Cross-link READMEs with GameOfLife and rule30 projects as one cellular-automata family.
- [x] Add opt-in JSON run metadata for reproducible sidecar and dimension discovery.

## Later

- [x] Connection to the Rule 30 open problem (`toy-projects/rule30`): use this generator as
  the visualization/experiment harness for center-column randomness checks.
  SPECULATIVE whether anything novel can be computed here — it's a toy.
- [x] Add a dependency-free radius-2 totalistic core with exhaustive rule and
  neighborhood coverage; full radius-2 non-totalistic rule tables remain deferred.

## Done

- 2026-08-22: custom `output_dir` support added; automaton output writes made atomic;
  output/cleanup assertions added to tests.
- Core implemented: 1D automaton generation with text output (`main.py`, `1d.py`),
  default Rule 30 demo.
- 2026-08-24: added a dependency-free CLI with explicit rule/step validation and a
  temporary-output regression test. [EMPIRICAL]
- 2026-08-25: added a dependency-free active-cell density helper over rendered rows;
  the text output contract and existing `run()` result remain unchanged. [EMPIRICAL]
- 2026-08-25: added opt-in structured JSON metrics with density and changed-cell
  activity over time via `--metrics`; text output and default behavior remain unchanged. [EMPIRICAL]
- 2026-08-25: added dependency-free batch rendering with complete pre-validation,
  ordered outputs, and optional metrics sidecars. [EMPIRICAL]
- 2026-08-25: centralized elementary-rule validation for single and batch runs;
  tests cover every accepted rule number from 0 through 255. [EMPIRICAL]
- 2026-08-25: linked the generator README to the related GameOfLife and Rule 30
  repositories; links are documentation-only and do not change runtime behavior. [EMPIRICAL]
- 2026-08-25: added root-scoped ignore rules for generated `test.json` and `output/`
  artifacts; existing local files were preserved. [EMPIRICAL]
- 2026-08-25: added opt-in dependency-free SVG sidecars for single and batch runs;
  text output and metrics remain unchanged unless explicitly requested. [EMPIRICAL]
- 2026-08-25: aligned single and batch Python API validation for `cell_size`, so
  invalid optional SVG settings fail before output-directory creation. [EMPIRICAL]
- 2026-08-25: added opt-in JSON run metadata for single and batch output;
  default text output and existing sidecars remain unchanged. [EMPIRICAL]
- 2026-08-25: documented Python 3.9+ as the supported runtime and added a
  regression check for the README contract. [EMPIRICAL]
- 2026-08-25: added a pure center-column extraction helper for rendered rows;
  it preserves the generator's seeded column convention without changing
  default output. [EMPIRICAL]
- 2026-08-25: added a pure radius-2 totalistic history core with 64 six-bit rules;
  existing output and APIs remain unchanged, and all rule/neighborhood pairs are
  exhaustively tested. [EMPIRICAL]
- 2026-08-25: added a standalone dependency-free totalistic CLI that emits the
  existing binary history as JSON on standard output; the elementary CLI and
  default files remain unchanged. [EMPIRICAL]
- 2026-08-25: added an opt-in self-describing totalistic metadata envelope via
  the API and CLI; raw history JSON and existing defaults remain unchanged.
  [EMPIRICAL]
- 2026-08-25: strengthened totalistic metadata with a canonical zero-padded
  six-bit rule string; raw history JSON remains byte-for-byte unchanged.
  [EMPIRICAL]
