"""Dependency-free CLI for radius-2 totalistic histories."""

import argparse
import json
import sys

from main import totalistic_history


def build_parser():
    parser = argparse.ArgumentParser(
        description="Print a radius-2 totalistic cellular-automaton history as JSON"
    )
    parser.add_argument(
        "--rule",
        required=True,
        type=int,
        help="six-bit totalistic rule number (0-63)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="positive number of generations (default: 100)",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        history = totalistic_history(args.rule, args.steps)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    json.dump(history, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
