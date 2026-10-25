# 0123 — Standalone standards child bounds

BG-056 host slice, 2026-09-07. Bound the isolated reference child to 30 seconds
through pipe draining and exit, with a combined 4 MiB stdout/stderr capture cap.
Retain separate raw prefixes, replay them after capture/cleanup, and distinguish
nonzero exit, timeout and overflow. On capture failure or Python interruption,
kill the owned child process group and reap the direct child before staged files
are removed. Keep private verified execution and release pins unchanged.

Use existing POSIX selector/group primitives without a new external dependency;
keep copied wrappers self-contained. Test raw-stream compatibility, real timeout,
overflow, nonzero exit, closed pipes with a live child, and staging cleanup.
Run focused and full repository checks. E-01–08 and existing internal-output
exception apply. No native/runtime/shared ABI change or sibling mutation.

Output delivery becomes buffered; cross-stream ordering is not preserved.
Parent startup/staging/I/O, blocked output sinks, escaped descendants, SIGKILL
and abrupt SIGTERM are not bounded by the child deadline. Trusted interpreter
closure and independent review remain open. Do not claim full process containment.

Validation: twenty-one focused tests pass (17 standard tests and four lock tests).
All ten gates pass in out/checks/run-wo5ygk7e. Three real standard stdout streams,
lock bytes and 24 native inputs are unchanged. Initial manual sentence formatting
warnings were corrected; all twelve final render/lint commands pass. The separate
Experience check passes after the output-timing adoption note. Evidence:
../evidence/standards-child-bounds-2026-09-07/README.md.
