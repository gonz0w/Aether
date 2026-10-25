# Exec bootstrap rejection cleanup — 2026-09-10

Six positive EOF/malformed startup cases pass through exact terminal observation
and two generations/six reclaims. Two deliberate broken implementations fail before
reclaim: validation bypass at2070, omitted backend stop at2072. All189 connections
cases, five launch cases and host checks (99 Python and five Rust descriptor tests)
pass on frozen final runtime sources. This is bounded producer evidence, not full
public execve, independent SDK/dash acceptance or release readiness.

## Behavior and ownership

EOF at0/16 bytes of bootstrap or survivor table and malformed bootstrap headers
produce source215; a malformed full table produces216. No application request may
precede rejection. The owner checks the published commit identity, observes the
source terminal, confirms backend/peer forced stop as raw144/kind3 and closes each
endpoint once before reclaim. Forced stops have no spontaneous terminal log lines.
The six positive serial logs contain source terminal records for both generations.
The malformed-table bypass reaches application read(0), proving the rejection check
is meaningful; the stop omission proves reclaim cannot precede containment.

Existing capability scopes, stack bounds and fixed RAM backend remain. There are
no kernel, SDK, sibling, dependency or released-pin changes. Cross-process shared
holders, unknown commit receipts and persistent filesystem recovery remain open.
The pre-code selection and simplicity assessment are in NATIVE-SHELL-STARTUP.md.

## Failures and corrective work

Attempt1 failed the older copy-inherit-completion-skip control: it rejected at1963
after three reclaims rather than zero. Its payload and kernel matched the earlier
passing run. Review found a real race between the empty queue read and terminal
query. The owner now requires a final EOF read after confirmed termination, when
the producer cannot append. The original zero-reclaim oracle is unchanged.
Attempt2 was interrupted with SIGINT to format this added check; host and launch
passed. Both attempts retain frozen sources, logs and full target artifacts.

Initial disk exhaustion prevented implementation edits/test launch. The maintainer
explicitly approved deletion of the single verified unpacked duplicate documented
in storage-recovery.md and duplicate-review.json. Its sealed archive, reports and
hashes remain untouched; no other qualification evidence was disposed.

## Reproduction and integrity

Commands, timing and exact tools are in the timing/results files. Use the existing
connections and launch commands documented in NATIVE-CONNECTIONS.md with the
recorded SDK/tools lock. run-sources records inputs at execution; sources additionally
captures final documentation. Archives are read back against their recorded hashes.
change.patch compares against the previous bootstrap-stalls packet. compatibility.json
checks all181 older cases: kernel load segments/entry remain identical, with only
.debug_line differences permitted; changed inheritance owner payloads reflect the
EOF race correction. Other prior payloads match outside developer entropy bytes.
qualification.json records exact artifact counts, changed files and owner sizes.
final-checks.json records final host, format, workflow, standards and diff checks.
The prior sealed manifest and the four-file simplicity snapshot are verified by
collect.py. manifest.json seals this packet, including both retained attempts.

Reader review and matching-revision consumer acceptance remain pending.
