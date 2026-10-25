# Owner structural fit and native cancellation checkpoint

2026-10-22 / BG-070 and UL-007/081/082. Implementation-agent review only.
[Pre-code review](../../../sys-init/docs/decisions/0211-owner-structural-fit.md),
[current contract](../../../sys-init/prototypes/native-filesystem-session/FORK.md),
[commands](../../../sys-init/prototypes/native-filesystem-session/README.md).

Private bounded description indices and the shared FILE operation boundary preserve
all capacities, authenticated process keys, wire bytes, structured errors, source
rights/offsets/flags and once-only cleanup. No dependency/allocator/service/channel/
worker/limit or default flag change. Old sealed inputs and released pins stay exact.

| Selection | Code bytes | Result |
| --- | ---: | --- |
| Exact prior composed roots, freshly rebuilt |18768 |48 tests, controls/strict builds pass; size rejects |
| Compact FILE state and shared operation boundary, same roots |18176 |49 tests including64 prior/current protocol schedules pass; size rejects |
| Direct fork decoder experiment |18368 |50 tests/155648 byte mutations/54 valid plans pass; largest fixed reservation968 vs536; reject/remove experiment |
| Final roots including actual native cancellation |18384 |50 tests/seven semantic omissions/two borrow denials and strict host/native builds pass; size rejects |

Target data observation is gate2240+workspace4096=6336 of8192, leaving1856.
The baseline gate was2968. Peer128/streams736 are named type observations, not
additional duplicates to add blindly; streams already reside inside the gate.
Largest observed final fixed subtraction536 is not a whole/peak-stack bound.
No native owner entry/control loop, complete resident/call graph or ISO is accepted.

Native cancellation explicitly consumes supervisor0, distinct from kernel-set
parent-11 and original copy errno. Stale sequence/phase causes no call; errors,
unknown values/unwind do not reopen or replay. Actual compiled root has23005,
source/token in rdi/rsi and unused operands zero; no extra pointer/unsafe block.
Host-injected results and disassembly do not prove native authority or settlement.

Final producer36 tests/15 compiling omissions and borrow denial pass, including
all13 description slots through occupancy/inheritance/flagged close. Default32
process tests, eight remote-description and nine FILE-wire tests and their direct
controls pass. FILE differential compares64 fault/delivery/padding schedules using
actual previous protocol code read from verified immutable local Git4e32ff296.
Reference source is host-only and is removed with generated outputs; no old runtime
is selected. There is no network fetch, copied SDK or binary/source archive.

Failures are retained compactly: first new occupancy test's borrow-check error;
a mistakenly broad test-helper replacement then causes destructor poisoning in
two omission runs. Restore every preexisting test byte from HEAD, keep only the
new test's counters outside mutex guards, and the complete producer controls pass.
The direct-codec test wrapper initially imports an unused fixture; strict warnings
correctly reject, then the corrected experiment passes before its size rejection.
No native persistence run or retry occurs. These are host/build failures, not a
successful native campaign or hidden reset. Original result hashes and short
failure excerpts remain; no transient source trees are retained.

Current workflow/quality/standards/static and source-identity/retention results are
recorded separately. Broad kernel/target/storage suites are not selected because
no complete admitted native owner exists. Next: coherent owner/entry/boot/native
copy/exec/wait/terminal/readiness/shutdown and full code/resident/peak-stack fit,
then a fresh scoped matching native qualification. No lower-bound theorem or quota
request follows from independent/composed roots; persistent Zsh/TTY/OpenZFS/native
packages/runner remains the R1 target, with no interim RAM shell image.

Nine current sys-init stages pass with unchanged inputs; historical native replay
is explicitly not run. Workflow175 groups/41 references/34 tools, userland offline
quality/pins, changed Rust format,1432 local destinations and final source identity
checks pass. Unsafe gate constructors and restored codec/router remain exact;
all preexisting process tests remain byte-identical before the appended new case.
cleanup.json records2545 generated files/299831296 allocated bytes
disposed, not a measured net-free-disk change. Retain compact JSON/short logs only;
no binaries/images, SDK copies or generated source trees. No native VM ran.
