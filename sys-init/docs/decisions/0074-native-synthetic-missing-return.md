# 0074 — Close synthetic missing-return schedules without inventing outcomes

Implemented synthetic schedule slice, 2026-09-06, BG-058/BG-057 IR-07.

Exercise Started-with-no-return using the real private start guards, deliberately
without invoking the corresponding Adapter operation. Creation starts with no
resources; launch starts after actual channel acquisition and retains that pair.
The fixture knows no missing operation executed. The driver keeps Started, pending
identity and unknown outcome, closes admission and never translates absence into
a native errno, successful application or cleanup. Counters count start transitions
in these schedules; they are not evidence of executed missing syscalls.

Two positives, missing-channel and missing-launch, must finish at 100/reclaimed=3.
Reject closure before Started or for another index without mutation. After closure,
retain original phase/token/pending state, no result/error/worker and unchanged
generations; deny start, application and further reservation. Only the launch
schedule has acquired a real pair. Its fixture disposes that pair using its explicit
knowledge that no launch call occurred; the closed driver does not claim recovery.
Three ordinary workers provide fixture accounting outside the closed driver.

Controls missing-skip-close, missing-invent-error and missing-forget-writer must
hit 1033/0, 1034/0 and 1035/0 respectively. The writer control uses the launch
schedule. All 84 previous cases retain their exact oracles. Keep the 4096-byte
bound, producer pin and toolchain unchanged; retain failures and fresh full evidence.

This is synthetic state-transition evidence executed in the native fixture. It
is not a lost kernel reply, delayed return, timeout, concurrent cancellation,
owner replacement or journal acknowledgment. If a synchronous kernel call never
returns, this owner cannot execute closure; a watchdog cannot qualify this test.
Started+closed retains unknown disposition without fabricating an errno. No public
recovery/cleanup interface is added. Next audit remaining ND-01 acceptance gaps
before selecting the ND-02 terminal-kind integration slice; BG-033 recovery stays open.

Applicable Foundations O-01/O-03/O-04, I-01/I-03–06, E-01–08 and Distribution
identity/recovery limits remain unchanged. No shared ABI, unsafe primitive,
dependency, output protocol, pin or exception changes. The trusted two-attempt,
one-pending-position bounds remain; no independent sign-off is claimed.

## Result and review

Decision 0074 passes 89 native cases, including IR-07 synthetic creation/launch
absence. The real start guards run but the selected syscall is deliberately
omitted. Closure retains Started, pending identity and unknown outcome; no invented
error or retry is accepted. Controls hit 1033/0, 1034/0 and 1035/0.
All 178 frozen inputs unchanged; 44 of 84 prior raw clients match, and changed
clients pass prior oracles. This is synthetic transition coverage executed in a
native fixture, not an actual lost kernel reply or recovery witness.
The binding acceptance review keeps remaining NB gaps explicit. Next: ND-02
terminal-kind contract against the frozen producer; ND-03–05 and BG-033 remain open.

start_launch is shared by the real receive path and synthetic schedule, as
start_channel already was. close_missing accepts only the matching pending Started
operation in the live owner. It preserves phase/resources and closes admission;
wrong index, Reserved and repeated closure deny without changing ownership. The
closed+Started state represents unknown disposition, not a received result.
There is no new errno, phase reset, queue, allocation or public recovery interface.
The existing selected-return application paths and native Adapter remain unchanged.

Creation absence performs no channel syscall. Launch absence performs actual
channel creation, then only the launch start transition. Its retained reader/writer
are checked before fixture disposal. The fixture's explicit no-call provenance
permits disposal; this is not a safe algorithm for an actually unknown launch.
Neither local counter value, clean Adapter accounting nor final 100/3 establishes
execution or reconciliation of the missing operation. No worker is manufactured.

One preflight source snapshot passes all 103 valid configuration builds. The full
89-case native run passes without a failed build or execution. Compiler flags,
linker bound and producer pin are unchanged. Three semantic controls distinguish
missing closure, invented rejection and forgotten writer from a passing result.
A generic timeout or missing tool cannot satisfy these assertions.

The [binding acceptance review](../research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md)
maps NB-01–09 to demonstrated scope and remaining BG/ND owners. The originally
planned audit is now complete in this bounded documentation scope. Next is the
ND-02 terminal-kind contract, not a claim that all ND-01 requirements are satisfied.
Native receipt identity, broader capacity/validation, event/journal composition and
real unknown-effect recovery retain their documented gaps.

Evidence: `docs/evidence/native-synthetic-missing-return-2026-09-06/`. The witness
retains exact inputs, command, raw clients and logs; review sources are separately
pinned. Documentation impact includes the audit, binding/receipt references,
standards adoption, native coverage, quality inventory and active work order.
No independent reviewer sign-off or full NB-09/recovery conformance is claimed.

## Validation — 2026-09-06

The full pinned native run passes 89 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 2752 (missing-channel), 3368
(missing-launch), 1456 (missing-skip-close), 1544 (missing-invent-error) and 1904
bytes (missing-forget-writer). All clients satisfy the unchanged 4096-byte bound.
All 103 local configuration builds and the full target run pass without failures.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-wo779a2_`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1293 historical outcomes
across 38 bundles and 16,323 listed files; these are not distinct current tests.
`git diff --check` and local reference link checks pass. Evidence is retained in
`docs/evidence/native-synthetic-missing-return-2026-09-06/`. Only validation notes
and final evidence copies follow checks; runtime sources, tests, inventory, catalog,
review findings and pins remain as checked. Next is ND-02 terminal-kind contract
work; the binding review retains remaining NB/ND and real recovery gaps.
