"""Dependency-free batch runner for elementary cellular automata."""

import argparse
import contextlib
import io
from pathlib import Path

from main import validate_rule, run


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


def run_batch(rules, no_steps=100, *, output_dir=None, metrics=False):
    """Render each unique rule after validating the complete batch.

    The individual renderer prints every row for compatibility with the
    existing API. Batch mode captures those rows and returns the renderer's
    per-rule count dictionaries, keeping the CLI output to one summary line.
    """
    values = _validate_rules(rules)
    _validate_steps(no_steps)
    results = {}
    for rule in values:
        with contextlib.redirect_stdout(io.StringIO()):
            results[rule] = run(
                rule,
                no_steps,
                output_dir=output_dir,
                metrics=metrics,
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
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rules = parse_rules(args.rules)
        run_batch(
            rules,
            args.steps,
            output_dir=args.output_dir,
            metrics=args.metrics,
        )
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(f"generated {len(rules)} rule outputs ({args.steps} steps each)")


if __name__ == "__main__":
    main()
