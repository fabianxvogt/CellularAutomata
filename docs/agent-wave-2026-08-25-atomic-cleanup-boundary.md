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
later cleanup pass; the primary failure is still reported. Each attempt first
checks the generated file's device/inode identity. If pathname reuse is
observed after a failed unlink, cleanup stops rather than deleting the
replacement object.

## Evidence

- Baseline full suite before the change: 58 tests passed.
- Failure-injection probe: `os.fsync()` raised `write failed` while temporary
  unlink raised `temporary cleanup failed`; the output remained byte-identical,
  the caller received `write failed`, and one temporary file remained.
- Follow-up probe: the first temporary unlink failed transiently, the bounded
  retry removed that exact temporary file, and the caller still received the
  primary `write failed` error.
- Path-reuse probe: a failed unlink replaced the generated pathname before the
  retry; the replacement file and an unrelated sibling were preserved, the
  primary `write failed` error remained deterministic, and no second unlink was
  attempted.
- Persistent-temp follow-up: after both exact-path cleanup attempts were
  forced to fail, a later successful rerun removed all three known stale
  sidecars but preserved the persistent temp file byte-for-byte and preserved a
  user-managed temp-like sibling. The later run's own temporary file was still
  replaced and removed normally.
- Output-directory probes: an existing regular file used as `output_dir` is
  rejected before output creation and preserved byte-for-byte; a directory at a
  known stale-sidecar path is not recursively removed, and its cleanup error is
  reported after the text output is written.
- Post-change checks: full suite, compilation, and `git diff --check` passed.

Classification: `INCREMENTAL / EMPIRICAL`.

This is a local error-reporting and bounded-cleanup hardening only. It does not
scan or delete unrelated directory entries, make multi-file sidecar updates
transactional, or establish automatic recovery when the filesystem refuses
both cleanup attempts. The identity check narrows pathname-reuse risk but does
not turn a check followed by unlink into a cross-filesystem compare-and-delete
transaction. A later run intentionally does not scan for old temp-like names:
after the original identity is lost, there is no safe way to distinguish a
failed-run artifact from an unrelated user file. Known sidecars remain
independently safe to clean because their paths are part of the output
contract.
