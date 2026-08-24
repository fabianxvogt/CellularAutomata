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

`--rule` accepts 0–255 and `--steps` must be positive. Invalid inputs fail
before an output file is created or replaced.

To keep generated files elsewhere, pass the keyword-only `output_dir` option:

```python
from pathlib import Path
from main import run

run(30, 100, output_dir=Path("/tmp/cellular-automata-output"))
```
