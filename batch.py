"""Dependency-free batch runner for elementary cellular automata."""

import argparse
import contextlib
import io
from pathlib import Path

from main import (
    DEFAULT_SVG_CELL_SIZE,
    _validate_option_flag,
    run,
    validate_cell_size,
    validate_rule,
)


def _validate_rules(rules):
    values = list(rules)
    if not values:
        raise ValueError("rules must contain at least one rule")
    try:
        for rule in values:
            validate_rule(rule)
    except TypeError as exc:
        raise TypeError("rules must contain integers from 0 through 255") from exc
    except ValueError as exc:
        raise ValueError("rules must contain integers from 0 through 255") from exc
    if len(set(values)) != len(values):
        raise ValueError("rules must not contain duplicates")
    return values


def parse_rules(spec):
    """Parse a comma-separated, ordered list of unique Wolfram rules."""
    if not isinstance(spec, str):
        raise TypeError("rule specification must be text")
    tokens = [token.strip() for token in spec.split(",")]
    if not spec.strip() or any(not token for token in tokens):
        raise ValueError("rules must be a comma-separated list of integers")
    try:
        rules = [int(token, 10) for token in tokens]
    except ValueError as exc:
        raise ValueError("rules must be a comma-separated list of integers") from exc
    return _validate_rules(rules)


def _validate_steps(no_steps):
    if isinstance(no_steps, bool) or not isinstance(no_steps, int):
        raise TypeError("no_steps must be a positive integer")
    if no_steps <= 0:
        raise ValueError("no_steps must be a positive integer")


def run_batch(
    rules,
    no_steps=100,
    *,
    output_dir=None,
    metrics=False,
    svg=False,
    cell_size=DEFAULT_SVG_CELL_SIZE,
    metadata=False,
):
    """Render each unique rule after validating the complete batch.

    The individual renderer prints every row for compatibility with the
    existing API. Batch mode captures those rows and returns the renderer's
    per-rule count dictionaries, keeping the CLI output to one summary line.
    Optional metrics, SVG, and metadata sidecars are forwarded to each rule
    renderer.
    """
    values = _validate_rules(rules)
    _validate_steps(no_steps)
    # Keep batch validation aligned with ``run`` so invalid optional sidecar
    # settings fail before the first rule can create an output file.
    metrics = _validate_option_flag(metrics, "metrics")
    svg = _validate_option_flag(svg, "svg")
    metadata = _validate_option_flag(metadata, "metadata")
    validate_cell_size(cell_size)
    results = {}
    for rule in values:
        with contextlib.redirect_stdout(io.StringIO()):
            results[rule] = run(
                rule,
                no_steps,
                output_dir=output_dir,
                metrics=metrics,
                svg=svg,
                cell_size=cell_size,
                metadata=metadata,
            )
    return results


def build_parser():
    parser = argparse.ArgumentParser(
        description="Render several 1D elementary cellular automata"
    )
    parser.add_argument(
        "--rules",
        required=True,
        help="comma-separated Wolfram rule numbers, for example 30,90,110",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="positive number of generations",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="directory for generated text output",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="write density and activity metrics beside each text output",
    )
    parser.add_argument(
        "--svg",
        action="store_true",
        help="write a dependency-free SVG visualization beside each text output",
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="write a JSON run-metadata sidecar beside each text output",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=DEFAULT_SVG_CELL_SIZE,
        help="SVG cell size in pixels (used with --svg; default: 4)",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.svg and args.cell_size != DEFAULT_SVG_CELL_SIZE:
        parser.error("--cell-size requires --svg")
    try:
        rules = parse_rules(args.rules)
        run_batch(
            rules,
            args.steps,
            output_dir=args.output_dir,
            metrics=args.metrics,
            svg=args.svg,
            cell_size=args.cell_size,
            metadata=args.metadata,
        )
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(f"generated {len(rules)} rule outputs ({args.steps} steps each)")


if __name__ == "__main__":
    main()
