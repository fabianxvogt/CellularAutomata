# CellularAutomata
Generate all rules for 1D Cellular Automata

Requires Python 3.9 or newer and uses only the Python standard library.

Run the default output behavior from the repository root:

```python
from main import run

run(30, 100)  # writes output/rule_30_output.txt
```

Or use the dependency-free command-line entry point:

```bash
python3 main.py --rule 30 --steps 100 --output-dir /tmp/cellular-automata-output
```

Add `--metrics` to write `rule_30_metrics.json` beside the text output. The
sidecar contains density and changed-cell activity for each generation, plus
their means.

Add `--svg` to write a dependency-free `rule_30_output.svg` visualization
beside the text output. `--cell-size` controls the square size of each cell:

```bash
python3 main.py --rule 30 --steps 100 --output-dir /tmp/cellular-automata-output --svg --cell-size 4
```

Add `--metadata` for an opt-in `rule_30_metadata.json` sidecar containing the
rule, rendered dimensions, enabled sidecar options, and output filenames. The
metadata option is recorded alongside the metrics and SVG flags. The default
text output is unchanged.

Render several rules in one bounded invocation with the dependency-free batch
runner:

```bash
python3 batch.py --rules 30,90,110 --steps 100 --output-dir /tmp/cellular-automata-batch --metrics --svg --metadata
```

Batch input is validated completely before any output is created; rule order is
preserved and duplicate rule numbers are rejected.

The Python renderers are `run(rule, no_steps=100, *, output_dir=None,
metrics=False, svg=False, cell_size=4, metadata=False)` and
`run_batch(rules, no_steps=100, *, output_dir=None, metrics=False, svg=False,
cell_size=4, metadata=False)`. The batch API accepts an ordered iterable of
rules; the CLI's `--rules` value is the comma-separated form.

The deferred neighborhood extension is available as a pure radius-2 totalistic
core. `totalistic_history(rule, no_steps=100)` accepts rules `0–63`, where bit `n`
controls a five-cell neighborhood containing `n` active cells, and returns the
seeded binary history without writing files. It uses fixed-dead boundaries;
the existing elementary `run()` default output and behavior are unchanged.

For a dependency-free command-line entry point, print the same history as JSON
to standard output:

```bash
python3 totalistic.py --rule 63 --steps 4
```

The totalistic CLI requires a rule from `0–63`, defaults `--steps` to `100`,
and does not create or modify files.

Add `--metadata` to wrap the history in a self-describing JSON object containing
the canonical six-bit rule string, rule encoding, radius, steps, width, seed
index, and fixed-dead boundary convention. The corresponding Python helper is
`totalistic_metadata(rule, no_steps=100)`. Without the flag, the raw history
JSON above is unchanged.

For API consumers, `totalistic_history_from_metadata(payload)` validates a
schema-v1 envelope and reproduces its history. It checks the declared rule,
dimensions, seed, boundary, encoding, and stored history; unknown extra fields
are allowed for forward-compatible readers.

`main.py` accepts `--rule` values `0–255`, `batch.py` accepts ordered `--rules`
in the same range, and `totalistic.py` accepts `--rule` values `0–63`. Step
counts must be positive. Invalid elementary inputs fail before an output file
is created or replaced; the totalistic CLI writes only to standard output. The
Python `run()` and `run_batch()` APIs also require boolean `metrics`, `svg`, and
`metadata` options and validate those options plus `cell_size` before creating
their output directory, even when SVG output is not requested.

To keep generated files elsewhere, pass the keyword-only `output_dir` option:

```python
from pathlib import Path
from main import run

run(30, 100, output_dir=Path("/tmp/cellular-automata-output"))
```

## Related projects

- [GameOfLife](https://github.com/fabianxvogt/GameOfLife) explores two-dimensional
  cellular automata and pattern evolution.
- [Rule 30](https://github.com/fabianxvogt/rule30) studies bounded successor checks
  and predictive-state experiments for the elementary Rule 30 family.
