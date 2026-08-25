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
original failure. Cleanup of the exact temporary path is attempted twice so a
transient unlink failure does not leave a stale file. If the operating system
still refuses removal, the uniquely named temporary file remains visible for a
later cleanup pass; the primary failure is still reported.

## Evidence

- Baseline full suite before the change: 58 tests passed.
- Failure-injection probe: `os.fsync()` raised `write failed` while temporary
  unlink raised `temporary cleanup failed`; the output remained byte-identical,
  the caller received `write failed`, and one temporary file remained.
- Follow-up probe: the first temporary unlink failed transiently, the bounded
  retry removed that exact temporary file, and the caller still received the
  primary `write failed` error.
- Output-directory probes: an existing regular file used as `output_dir` is
  rejected before output creation and preserved byte-for-byte; a directory at a
  known stale-sidecar path is not recursively removed, and its cleanup error is
  reported after the text output is written.
- Post-change checks: full suite, compilation, and `git diff --check` passed.

Classification: `INCREMENTAL / EMPIRICAL`.

This is a local error-reporting and bounded-cleanup hardening only. It does not
scan or delete unrelated directory entries, make multi-file sidecar updates
transactional, or establish automatic recovery when the filesystem refuses
both cleanup attempts.
