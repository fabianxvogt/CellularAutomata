# Atomic temporary cleanup boundary

## Scope

Bounded audit of the elementary renderer's sidecar cleanup and atomic-write
failure paths after the current sidecar error-handling fixes. No output schema,
transaction design, or batch contract was changed.

## Finding

`_write_output_atomically()` preserves the existing destination until the
temporary file is fully flushed and replaced. Before this audit, if the write
or replacement failed and removing the temporary file also raised an
`OSError`, the cleanup exception masked the primary failure. The destination
remained unchanged, but callers received misleading error information.

The cleanup path now suppresses only that secondary `OSError` and re-raises the
original failure. If the operating system cannot remove the uniquely named
temporary file, the file remains visible for a later cleanup pass; the primary
failure is still reported.

## Evidence

- Baseline full suite before the change: 58 tests passed.
- Failure-injection probe: `os.fsync()` raised `write failed` while temporary
  unlink raised `temporary cleanup failed`; the output remained byte-identical,
  the caller received `write failed`, and one temporary file remained.
- Post-change checks: full suite, compilation, and `git diff --check` passed.

Classification: `INCREMENTAL / EMPIRICAL`.

This is a local error-reporting hardening only. It does not make multi-file
sidecar updates transactional and does not establish automatic recovery when
the filesystem refuses cleanup.
