# Self-describing radius-2 totalistic metadata — 2026-08-25

## Scope

Added the pure `totalistic_metadata(rule, steps)` API helper and opt-in CLI
`--metadata` flag. The JSON-compatible payload records schema version, radius,
canonical zero-padded six-bit rule string, rule, steps, rendered width, seed
index, fixed-dead boundary behavior, and the generated history. The default
CLI still emits the raw history JSON and does not write files.

The API also exposes `totalistic_history_from_metadata(payload)` for
schema-v1 round trips. It regenerates the history and rejects mismatched rule,
encoding, dimensions, seed, boundary, or stored-history fields. Unknown fields
are intentionally ignored so a reader can tolerate additive metadata.

## Evidence

- API tests verify the metadata contract and exact seeded history.
- Metadata tests verify that low-valued rules retain leading zero bits in the
  canonical rule string.
- CLI tests verify the metadata envelope and byte-for-byte preservation of the
  default raw JSON output.
- Round-trip tests verify a JSON serialize/parse cycle, additive fields, and
  rejection of tampered contract fields.
- The feature uses only the Python standard library.

## Limits

This validator supports only schema version 1 and the current radius-2,
fixed-dead convention. It validates the complete generated history against the
declared rule and step count, but it does not validate or interpret unknown
extension fields.

## Classification

`INCREMENTAL`, `EMPIRICAL`. This is a bounded reproducibility aid; it makes no
claim about complexity, randomness, or novelty.
