# Native suspend integration

Prospective implementation: opt-in BSP single-context terminal-derived SIGCHLD
and public sigsuspend, following NATIVE-SHELL-STARTUP's selected contract. Kernel
parent provenance selects the generation-checked recipient; no arbitrary post API.
Preserve retained status and ordinary profiles. Validate pointers before masks;
serialize temporary mask/peek/park under IF=0. Clear suspension on handler or stop.
First witness tests pending-before-entry, invalid inputs and original-mask return,
then unchanged wait.sh tests child-terminal wakeup. Disabled routing must reject
at the caller probe. Further stale-parent/stop/race controls remain required before
broad adoption. No sibling or pin modifications. New state is one optional saved
mask in an opt-in domain; single-context only. Frame helper owns no pending state.
Reuse pending bits and codec; no extra service or remote-post protocol (SE-01–05).
Select focused native tests, host/format and scheduler regression; retain failures.

First focused attempt: real wait.sh completed helper7/parent0/backend17 twice and
six reclaims, including the pending-before-entry libc check. The harness selected
a generic normal-child72 lifecycle oracle rather than helper7/parent0 for the new
label. Add that exact label to the existing null lifecycle oracle; retain this
harness integration failure and its sources. Disabled routing was not yet run.

First native scope is handler-only suspension: an eligible unsupported non-handler
default returns ENOTSUP with original mask restored and pending occurrence retained.
Default termination while suspended remains a gap against the broader design;
no successful no-op or fake EINTR is introduced. Actual wait success alone does not
prove both forced race orders, stale-parent rejection or stop-while-parked. Those
controls remain required before full adoption.

The first M4 scheduler regression attempt failed before boot because the sandbox
blocked its private QMP Unix socket (Operation not permitted). It is retained as
an infrastructure failure, not a guest regression. Retrying the unchanged sources
with approved local socket access passed all seven cases. The corrected focused
native run passes both wait and disabled-route cases. No source change or timeout
was used to make either expected rejection pass.

## Results

PASS: 303 connections cases in 953.60s, both focused profiles, seven M4
scheduler cases and 101 host Python tests plus Zig/pin checks. The unchanged script
SHA-256 is 087a4dbd0db86924288781ddb6f0f7c72336296b4ed253c0d59add6e374396f5.
Its helper exits7, dash exits0, backend exits17, twice, with exact wait-output bytes
and six reclaims. Missing routing yields parent233/owner1950 with zero reclaims.
Formatting passes and 265 runtime/source inputs remain frozen across final runs.
All failed attempts and their artifacts/source revisions are retained.

578/879 compared prior ELF/raw/kernel artifacts are identical;
compatibility.json names any changed bytes. The full artifact archives include
build commands, tools/SDK identities, serial logs and results; inputs are pinned,
not pulled from mutable sibling checkouts. No independent owner approval is claimed.

Remaining coverage: deterministic post-after-park ordering (the real script does
not force this schedule), stale parent replacement, repeated terminal, blocked or
ignored lifecycle signals, stop/reclaim while parked, native bad-handler failure,
nested delivery and default termination. The selected initial default-effect
ENOTSUP behavior is narrower than the broader design. Before full consumer handoff,
complete these controls and matched command-runner qualification. No R1, installed
SDK, physical hardware or general POSIX claim follows from this first script pass.
