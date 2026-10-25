# UL-007 repeated commands and descriptor redirection — 2026-09-11

**PASS: 254 native cases, 12 independent serial protocols, and host checks including
99 Python tests.** Actual dash executes three external commands in one parent,
redirects a builtin to stderr, restores stdout, collects/reclaims each child and
exits with complete cleanup. One local attempt passed; no failed or retried local
native run. Producer failures remain retained as historical evidence.

The native selection is 247 connections/process cases, five launch and two console
cases. [Execution receipt](results.json), per-profile results and raw logs retain
exact commands, tools, flags, ABI and artifacts. [Serial checks](serial-checks.json)
compare expected and observed terminals, supervisors, panics and ordered host writes
for six new and six prior protocols. All started processes have complete owned
cleanup; all 579 source and 4311 SDK file hashes remain unchanged.

## Qualified behavior

One shell at parent generation 1 runs children at generations 1,2,3. Each child exits 72;
terminal observation plus wait acknowledgment precedes task disposal and slot reuse.
Fresh routes/bootstrap references and advancing parent freeze tokens are checked.
Old token and old bootstrap controls reject on the second child with exactly one
prior reclaim. The parent and one exclusive UART backend remain alive throughout.

Dash executes `echo redirected >&2; /next`, then `echo restored; /next`, then `/next`.
After the third child, a later host command `echo $?;exit 0` prints 72 and closes the
streams. Four prompts, seven ordered host writes, three child 72 terminals, parent 0,
backend/probe17 and six reclaims pass. Owner assertions require logical stream byte
counts 72/60/19; the shared physical UART alone does not distinguish stdout/stderr.

Fork and exec snapshots now leave absent entries canonically zero while preserving
validation of live presence, flags, counts and references. Inactive local metadata
cannot revive a closed descriptor. Raw fork/exec encodings reject at owner 2150/2120,
with redirected builtin output but no CHILD READY and zero reclaims. Existing FD10
CLOEXEC and previous shell-session controls remain regressions. This qualifies
inherited-descriptor redirection, not filesystem redirection or general pipelines.

All twelve selected owner images fit the unchanged ABI18 16 KiB bound; [maximum is
9944 bytes](owner-sizes.json). Kernel/build, upstream configured dash objects, SDK,
shared FD facade, quotas and released pins are unchanged. The earlier 55 init-bound
results are reused by kernel identity, not rerun or counted in this 254-case result.
No fresh SMP/M4 or whole-kernel qualification is claimed.

## Provenance and reproduction

Selected producer manifest SHA256:
`d1ecc967cddf1cea919f430d020236036a99e7cf34209a80d764d1470ef27601`.
All 53 entries were verified before consumption. producer-packet/ retains frozen
sources, exact producer receipts and its failed first native attempt; the verified
top-level target archive is omitted as recorded in packet-retention.json.
[Earlier repeat history and pipe references](producer-history/inventory.json)
retain their own failures, source snapshots and scope limits.

Run `python3 -B docs/evidence/dash-redirect-consumer-2026-09-11/run.py` with the pinned
local dependencies. Python 3.14.7, bounded process helper, fixed PATH/LC_ALL/private
TMPDIR and original 30-second guest watchdogs are recorded. Connections 1800,
launch/console 300 and host 600-second deadlines, 512 MiB per output stream. Private
output is build/dash-redirect-consumer-jdaq9fdz. The driver verifies the SDK/musl
archive/tools and preserves the native source snapshot. It includes the previously
pinned host inventory document and absolute Zig path before testing, incorporating
prior intake corrections without rewriting earlier evidence.

[Pre-execution review](review.md), [input comparison](intake.json) and review-inputs/
record the twelve changed frozen paths plus the known host-document completion.
No sibling source edits, real-prefix installation, new source fetch, default SDK
adoption or monitoring. Source provenance hashes are not source authentication or
independent security/reader review; UL-016/061–063/081 remain open.

## Next work

[Pipe consumer intake](pipe-next.md) maps the next producer delivery to the existing
DASH-substitution requirements. At capture the pipe core is host-tested and compiles
without std; native dispatcher/adapter/fork-plan/endpoint wiring remains unqualified.
EOF must follow confirmed last-writer termination before dash waits, while task
reclamation remains a separate collection step. Native backpressure, reply failure,
alias/CLOEXEC, stale-generation and SIGPIPE controls precede substitution acceptance.
A smaller builtin-only example cannot replace the unchanged helper workload.

The existing twelve-script matrix, concurrent pipelines, filesystem redirection,
arbitrary executable lookup, human-paced TTY/jobs and sys-init/persistent/package
assembly remain separate. This advances UL-007; full M3 is not complete.

Final [acceptance](acceptance.json): driver/receipt identities, source/SDK integrity,
serial protocols, Python syntax and tracked whitespace pass. [Local quality output](quality.log)
passes the pin/documentation inventory gate. Independent reviews/publication remain
separate. SHA256SUMS binds the retained bytes, including producer failure history.
