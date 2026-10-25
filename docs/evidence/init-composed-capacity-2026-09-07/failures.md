# Attempts

Setup failed before building because the private parent was absent; setup-attempt.json records it. Attempt 1 passed host and format checks but target compilation rejected a runtime-selected comptime format string. No target ran. Sources, logs and outputs are retained in attempt-1.tar.gz. The fix supplies the profile name as a string argument to a fixed format; marker bytes remain as specified.

The reused SI-05 SDK archive failed safe extraction because obj/Makefile contained an absolute symlink. The original archive and partial extraction remain retained. The new packet rewrites only that link to ../musl-1.2.6/Makefile, preserving the same target bytes within the archive. Safe extraction then passes; no compiler/runtime input bytes change.

Attempt 2 passed every native suite and all host/format checks, but M4 QEMU could not bind its local QMP socket under the filesystem sandbox (Operation not permitted). No M4 boot occurred. The source-matched failure, ISO, QEMU log and receipt are retained in sandbox-regression-failure.tar.gz. Only that suite is retried with socket permission; completed.json composes unchanged-source passing checks with the new M4 receipt and retains the failed command separately. No source fix or blanket rerun is required for this infrastructure failure.
