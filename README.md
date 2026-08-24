# CellularAutomata
Generate all rules for 1D Cellular Automata

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

Render several rules in one bounded invocation with the dependency-free batch
runner:

```bash
python3 batch.py --rules 30,90,110 --steps 100 --output-dir /tmp/cellular-automata-batch --metrics
```

Batch input is validated completely before any output is created; rule order is
preserved and duplicate rule numbers are rejected.

`--rule` accepts 0–255 and `--steps` must be positive. Invalid inputs fail
before an output file is created or replaced.

To keep generated files elsewhere, pass the keyword-only `output_dir` option:

```python
from pathlib import Path
from main import run

run(30, 100, output_dir=Path("/tmp/cellular-automata-output"))
```
