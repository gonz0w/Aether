# Unchanged consumer descriptor closure — 2026-09-13

Requirement: actual dash executes unchanged fd-closure.sh, launches the pinned
helper's `closed` mode through real fork/exec/wait and prints `closed ok\n` only
when that helper finds descriptors3–63 closed. Preserve manifest environment,
FD10 CLOEXEC filtering, native statuses, output readback and six reclaims.

Dependency selection: wait.sh backgrounds its child. Pinned dash forkchild opens
/dev/null after closing stdin for FORK_BG; the current private exec fixture has no
openable null descriptor route. fd-leak-control.sh also requires writable /scratch.
Do not change either script, alias ordinary input as /dev/null, or claim those
workloads pass. Select the independent closure workload first.

Aether owns bounded enforcement/adapters; userland owns compatibility and acceptance.
Reuse the existing argument workload's helper image/startup validation, descriptor
table, fixed helper route and zero-status lifecycle. Add only a closure selection
and two controls: inject a descriptor alias after replacement startup so the real
helper returns95; corrupt delivered wait status so dash rejects with22. These are
fixture controls, not implemented writable redirection or the consumer leak script.

Forbidden: skipped helper accepted as evidence of closure, fabricated output,
missing cleanup, weakened CLOEXEC/authority checks, altered consumer inputs,
increased quotas, sibling/pin/evidence edits or full-dash claims. Check exact script,
helper/manifest hashes and actual source call; the leak control must fail at the
real helper. Existing exec table controls continue covering publication rejection.

No kernel/ABI/service/unsafe boundary change. The alias control uses existing
single-context descriptor operations; borrowed startup buffers and transport
ownership remain unchanged. Simplicity: reuse the bounded helper route instead of
adding a new service or general descriptor abstraction. No consumed path retired.
Select focused three-case native coverage, complete connections, host/harness/pin
checks, C/Rust formatting and separate simplicity verification. Freeze runtime
sources per run, retain all failures and update native contracts/workflow/STATE.

First preflight: positive target passes with child0/parent0/backend17 twice and six reclaims, but the host lifecycle selector lacks the new closure label. Preserve that failed attempt and inputs; extend only the exact positive label selection. Also correct the planned status-control oracle: dash takes its exit22 path, but final stdout closure is rejected by independent missing-output readback2310 before parent terminal publication. Require child0/owner2310 and zero reclaims, not an unobservable parent terminal. No target source changes for either oracle correction.

## Qualified result

PASS: all 290 connections cases and the final three-case focused preflight.
Host checks, scoped C/Rust formatting, workflow/released pins and the separate
simplicity manifest/members pass. All 258 runtime/test files stayed
frozen; the harness binds 244 sources. Archives retain both
preflights and the full final target run, verified member by member.

Actual dash executes the exact pinned script with WITNESS=value, LC_ALL=C,
PATH=/nonexistent and granted PWD=/work. The unchanged helper observes descriptors
3–63 closed after real exec, including the fixture's prior FD10 CLOEXEC alias.
Child0/parent0/backend17 repeat with six reclaims; the owner independently reads
back exactly 10 bytes of closed ok plus newline, with no stdin/stderr traffic.
Injected FD3 is detected by the real helper (95/owner2130). Corrupt wait status
prevents the success line and fails owner2310 after child0, before the parent's
exit22 can be published. Both controls reclaim zero.

Closure owners: [9336, 9336, 9336] bytes, within 16,384.
Of 547 previous ELF/raw images, 547 are unchanged;
compatibility.json names every changed image, covered by the full suite. The source
delta and original failed lifecycle-selector attempt remain explicit. No kernel,
ABI, SDK, sibling, dependency version, quota or released-pin changes.

Reproduce with the existing `scripts/launch_smoke.py --connections` invocation in
connections-final.json, the pinned SDK and tool lock; use fresh output locations.
sources.tar.gz binds final code, implementation.diff is relative to the matched
phase-one packet. The collector's fixed output names are historical recipes;
change destinations before reuse and never overwrite sealed evidence.

This is producer qualification of DASH-fd-closure, not independent userland
acceptance, writable fd-leak-control, the complete twelve-workload gate or R1.
Next define scoped /dev/null descriptor ownership and fork/exec lifetime for the
unchanged background wait script. Keep failed-exec and writable /scratch leak/
redirection workloads explicit; do not substitute a fabricated local file route.
