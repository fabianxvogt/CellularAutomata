# Self-describing radius-2 totalistic metadata — 2026-08-25

## Scope

Added the pure `totalistic_metadata(rule, steps)` API helper and opt-in CLI
`--metadata` flag. The JSON-compatible payload records schema version, radius,
canonical zero-padded six-bit rule string, rule, steps, rendered width, seed
index, fixed-dead boundary behavior, and the generated history. The default
CLI still emits the raw history JSON and does not write files.

## Evidence

- API tests verify the metadata contract and exact seeded history.
- Metadata tests verify that low-valued rules retain leading zero bits in the
  canonical rule string.
- CLI tests verify the metadata envelope and byte-for-byte preservation of the
  default raw JSON output.
- The feature uses only the Python standard library.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a bounded reproducibility aid; it makes no
claim about complexity, randomness, or novelty.
