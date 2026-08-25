import argparse
import json
import os
import tempfile
from pathlib import Path


MIN_RULE = 0
MAX_RULE = 255
MIN_TOTALISTIC_RULE = 0
MAX_TOTALISTIC_RULE = 63
DEFAULT_SVG_CELL_SIZE = 4


def validate_rule(rule):
    """Validate and return one elementary Wolfram rule number."""
    if isinstance(rule, bool) or not isinstance(rule, int):
        raise TypeError("rule must be an integer from 0 through 255")
    if not MIN_RULE <= rule <= MAX_RULE:
        raise ValueError("rule must be an integer from 0 through 255")
    return rule


def validate_totalistic_rule(rule):
    """Validate a radius-2 binary totalistic rule encoded in six bits."""
    if isinstance(rule, bool) or not isinstance(rule, int):
        raise TypeError("totalistic rule must be an integer from 0 through 63")
    if not MIN_TOTALISTIC_RULE <= rule <= MAX_TOTALISTIC_RULE:
        raise ValueError("totalistic rule must be an integer from 0 through 63")
    return rule


def _validated_binary_state(state):
    """Return a non-empty, independent copy of a binary state."""
    try:
        values = list(state)
    except TypeError as exc:
        raise TypeError("state must be an iterable of binary cell values") from exc
    if not values:
        raise ValueError("state must contain at least one cell")
    if any(isinstance(cell, bool) or cell not in (0, 1) for cell in values):
        raise ValueError("state must contain only binary cell values")
    return values


def totalistic_step(state, rule):
    """Return one fixed-boundary radius-2 totalistic generation.

    The five-cell neighborhood is reduced to its active-cell count. Bit ``n``
    of ``rule`` is the result for count ``n`` (counts range from 0 through 5).
    Cells without a complete radius-2 neighborhood remain dead, matching the
    existing generator's fixed-dead boundary convention.
    """
    rule = validate_totalistic_rule(rule)
    values = _validated_binary_state(state)
    new_state = [0] * len(values)
    for index in range(2, len(values) - 2):
        active_count = sum(values[index - 2:index + 3])
        new_state[index] = (rule >> active_count) & 1
    return new_state


def totalistic_history(rule, no_steps=100):
    """Return seeded history for a radius-2 totalistic rule without writing files."""
    validate_totalistic_rule(rule)
    if isinstance(no_steps, bool) or not isinstance(no_steps, int):
        raise TypeError("no_steps must be a positive integer")
    if no_steps <= 0:
        raise ValueError("no_steps must be a positive integer")

    width = no_steps * 2
    state = [0] * width
    state[no_steps] = 1
    history = [state]
    for _ in range(no_steps - 1):
        state = totalistic_step(state, rule)
        history.append(state)
    return history


def totalistic_metadata(rule, no_steps=100):
    """Return a self-describing JSON-compatible totalistic history payload."""
    rule = validate_totalistic_rule(rule)
    history = totalistic_history(rule, no_steps)
    return {
        "schema_version": 1,
        "radius": 2,
        "rule": rule,
        "rule_bits": format(rule, "06b"),
        "rule_encoding": "bit n = output for n active cells",
        "steps": no_steps,
        "width": len(history[0]),
        "seed_index": history[0].index(1),
        "boundary": "fixed-dead",
        "history": history,
    }


def _write_output_atomically(output_path, lines):
    """Replace ``output_path`` only after the complete output is written."""
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            for line in lines:
                temporary_file.write(line + "\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, output_path)
    except BaseException:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def _validated_rows(lines):
    """Return equally sized, non-empty text-output rows and their width."""
    rows = list(lines)
    if not rows:
        raise ValueError("lines must contain at least one row")
    if any(not isinstance(row, str) for row in rows):
        raise TypeError("lines must contain strings")

    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("lines must contain equally sized, non-empty rows")
    allowed_markers = {" ", "0", "■"}
    if any(marker not in allowed_markers for row in rows for marker in row):
        raise ValueError("lines contain a character outside the text output format")
    return rows, width


def validate_cell_size(cell_size):
    """Validate and return the pixel size used for SVG cells."""
    if isinstance(cell_size, bool) or not isinstance(cell_size, int):
        raise TypeError("cell_size must be a positive integer")
    if cell_size <= 0:
        raise ValueError("cell_size must be a positive integer")
    return cell_size


def active_cell_density(lines):
    """Return the fraction of rendered cells marked active.

    ``lines`` are rows from the text output. ``■`` is active; spaces and the
    legacy ``0`` padding marker are inactive. The helper is pure and does not
    read or modify files.
    """
    rows, width = _validated_rows(lines)
    active_cells = sum(row.count("■") for row in rows)
    return active_cells / (len(rows) * width)


def center_column(lines):
    """Return the center-cell states as a binary string.

    The generator seeds the right-hand center column for its even-width
    rendered rows, so ``width // 2`` preserves the initial-condition column.
    """
    rows, width = _validated_rows(lines)
    center_index = width // 2
    return "".join("1" if row[center_index] == "■" else "0" for row in rows)


def render_metrics(lines):
    """Return dependency-free density and activity metrics for rendered rows.

    Activity is the fraction of cells that changed from the previous row;
    generation zero has no predecessor and is therefore reported as ``0.0``.
    """
    rows, width = _validated_rows(lines)
    density_over_time = [row.count("■") / width for row in rows]
    activity_over_time = [0.0]
    for previous, current in zip(rows, rows[1:]):
        changed_cells = sum(left != right for left, right in zip(previous, current))
        activity_over_time.append(changed_cells / width)

    return {
        "activity_over_time": activity_over_time,
        "density_over_time": density_over_time,
        "mean_activity": sum(activity_over_time) / len(activity_over_time),
        "mean_density": sum(density_over_time) / len(density_over_time),
        "steps": len(rows),
        "width": width,
    }


def render_metadata(
    rule,
    lines,
    *,
    metrics=False,
    svg=False,
    cell_size=DEFAULT_SVG_CELL_SIZE,
    metadata=False,
):
    """Return dependency-free metadata describing one rendered run."""
    rule = validate_rule(rule)
    rows, width = _validated_rows(lines)
    cell_size = validate_cell_size(cell_size)
    return {
        "schema_version": 1,
        "rule": rule,
        "steps": len(rows),
        "width": width,
        "options": {
            "cell_size": cell_size,
            "metrics": bool(metrics),
            "svg": bool(svg),
        },
        "outputs": {
            "text": f"rule_{rule}_output.txt",
            "metrics": f"rule_{rule}_metrics.json" if metrics else None,
            "svg": f"rule_{rule}_output.svg" if svg else None,
            "metadata": f"rule_{rule}_metadata.json" if metadata else None,
        },
    }


def render_svg(lines, *, cell_size=DEFAULT_SVG_CELL_SIZE):
    """Return a dependency-free SVG visualization of rendered automaton rows."""
    rows, width = _validated_rows(lines)
    cell_size = validate_cell_size(cell_size)
    svg_width = width * cell_size
    svg_height = len(rows) * cell_size
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {svg_width} {svg_height}" '
            f'width="{svg_width}" height="{svg_height}" '
            'role="img" aria-labelledby="title" '
            'shape-rendering="crispEdges">'
        ),
        '<title id="title">Elementary cellular automaton</title>',
        f'<rect width="{svg_width}" height="{svg_height}" fill="#ffffff"/>',
    ]
    for row_index, row in enumerate(rows):
        for column_index, marker in enumerate(row):
            if marker == "■":
                svg_lines.append(
                    f'<rect x="{column_index * cell_size}" '
                    f'y="{row_index * cell_size}" '
                    f'width="{cell_size}" height="{cell_size}" '
                    'fill="#111827"/>'
                )
    svg_lines.append("</svg>")
    return "\n".join(svg_lines) + "\n"


def run(
    rule,
    no_steps=100,
    *,
    output_dir=None,
    metrics=False,
    svg=False,
    cell_size=DEFAULT_SVG_CELL_SIZE,
    metadata=False,
):
    """Run a one-dimensional cellular automaton for ``no_steps`` generations.

    ``rule`` is an eight-bit Wolfram rule number and ``no_steps`` must be a
    positive integer. ``output_dir`` optionally selects the directory for the
    generated output and is keyword-only to preserve positional compatibility.
    When ``metrics`` is true, write a JSON sidecar containing density and
    activity over time. When ``svg`` is true, write a dependency-free SVG
    sidecar; ``cell_size`` controls the square size of each rendered cell.
    When ``metadata`` is true, write a JSON sidecar describing the run and
    requested output files.
    Validate these public inputs before creating output so invalid requests
    fail without partial files or misleading output.
    """
    validate_rule(rule)
    if isinstance(no_steps, bool) or not isinstance(no_steps, int):
        raise TypeError("no_steps must be a positive integer")
    if no_steps <= 0:
        raise ValueError("no_steps must be a positive integer")
    # Validate the complete public input contract before creating the output
    # directory, even when SVG output is disabled. This prevents a typo in a
    # future opt-in flag from being silently accepted by the Python API.
    validate_cell_size(cell_size)

    # Define the initial state, typically a single active cell in the middle
    initial_state = [0] * no_steps * 2
    initial_state[no_steps] = 1

    # Define the rule as an 8-bit binary number, e.g., 30 for Rule 30
    binary_rule = f'{rule:08b}'

    # Create a dictionary to map neighborhood patterns to new cell states
    rule_dict = {}
    count_dict = {}
    for pattern in range(7, -1, -1):
        rule_dict[format(pattern, '03b')] = binary_rule[7 - pattern]
        count_dict[format(pattern, '03b')] = 0

    # Initialize the list to store the automaton's history
    automaton_history = [initial_state]

    # Generate the automaton's history
    for _ in range(no_steps - 1):
        current_state = automaton_history[-1]
        new_state = [0] * no_steps * 2

        # Apply the rule to determine the new state
        for i in range(1, no_steps * 2 - 1):
            neighborhood = ''.join(map(str, current_state[i - 1:i + 2]))
            new_state[i] = int(rule_dict.get(neighborhood, '0'))
            count_dict[neighborhood] += 1

        automaton_history.append(new_state)

    # Write the automaton's history to a text file with leading zeros
    output_dir = Path("output") if output_dir is None else Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_lines = []
    for state in automaton_history:
        line = ''.join(map(str, state))
        line = line.replace('0', ' ')
        line = line.replace('1', '■')
        line = line.rjust(no_steps, '0')
        print(line)
        output_lines.append(line)
    _write_output_atomically(output_dir / f"rule_{rule}_output.txt", output_lines)
    if svg:
        _write_output_atomically(
            output_dir / f"rule_{rule}_output.svg",
            render_svg(output_lines, cell_size=cell_size).splitlines(),
        )
    if metrics:
        metric_lines = json.dumps(
            render_metrics(output_lines), indent=2, sort_keys=True
        ).splitlines()
        _write_output_atomically(output_dir / f"rule_{rule}_metrics.json", metric_lines)
    if metadata:
        metadata_lines = json.dumps(
            render_metadata(
                rule,
                output_lines,
                metrics=metrics,
                svg=svg,
                cell_size=cell_size,
                metadata=metadata,
            ),
            indent=2,
            sort_keys=True,
        ).splitlines()
        _write_output_atomically(output_dir / f"rule_{rule}_metadata.json", metadata_lines)

    #print(count_dict)
    return count_dict

def build_parser():
    parser = argparse.ArgumentParser(description="Render a 1D elementary cellular automaton")
    parser.add_argument("--rule", type=int, default=30, help="Wolfram rule number (0-255)")
    parser.add_argument("--steps", type=int, default=100, help="positive number of generations")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="directory for the generated text output",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="write density and activity metrics as JSON beside the text output",
    )
    parser.add_argument(
        "--svg",
        action="store_true",
        help="write a dependency-free SVG visualization beside the text output",
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="write a JSON run-metadata sidecar beside the text output",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=DEFAULT_SVG_CELL_SIZE,
        help="SVG cell size in pixels (used with --svg; default: 4)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.svg and args.cell_size != DEFAULT_SVG_CELL_SIZE:
        build_parser().error("--cell-size requires --svg")
    try:
        run(
            args.rule,
            args.steps,
            output_dir=args.output_dir,
            metrics=args.metrics,
            svg=args.svg,
            cell_size=args.cell_size,
            metadata=args.metadata,
        )
    except (TypeError, ValueError) as exc:
        parser = build_parser()
        parser.error(str(exc))


if __name__ == "__main__":
    main()

# Example usage:
# for i in range(1, 256):
#     count_dict = run(i, 200)  # Run Rule for n steps and store the result in "rule_<ruleNo>_output.txt"
#     uses_all_conditions = True
#     for key in count_dict:
#         if count_dict[key] == 0:
#             uses_all_conditions = False

#     if uses_all_conditions:
#         print(f"RULE {i}")
