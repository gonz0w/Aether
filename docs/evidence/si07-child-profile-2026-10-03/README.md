# Native SI-07 child profile qualification — 2026-10-03

Before-code requirement: exercise both child-bootstrap mismatch directions in
real AENSI001/ABI22 executions using the sealed v1/v2 parent and bytecount ELFs.
Keep parent/owner matched so rejection is attributable to the child bootstrap.
Also run both matching one-cycle controls. Original owner/sys-init/kernel sources,
ABI, grants, quotas, released pins and earlier evidence remain unchanged.

Mismatch oracle: bytecount exits120/kind1 without submitting any I/O request;
owner verifies admission/bootstrap occurred, zero child frame/positions, EOF on
child reply, and untouched backend output. A private test observer then stops and
observes the runner, closes all live references/endpoints, reclaims child/runner,
observes backend17 and reclaim, verifies stale handles and obtains authorized halt
with exactly three reclaims. No generic panic/timeout counts as rejection. Matched
controls complete exact6-newline, statuses0/0/17 and three reclaims/halt. Test observer
cleanup is not new sys-init recovery policy or proof of arbitrary cancellation.

Authority/security: use only real successful launch handles and owned endpoints.
Never publish a malformed binding as native authority; v1/v2 selectors remain
connection-local. Fixed borrowed trap buffers are live through synchronous calls.
No new unsafe block, dependency, resource limit or public interface is introduced.
Freeze sources for runs, retain all failed attempts and inspect linked code/stack.
Required checks: native traces and semantic corruption controls, raw/ELF binding,
scoped stack/builtin inspection, host/pin/workflow/Experience and local links.

Simplicity: isolated observer branches in copied fixture sources provide exact
failure observations without duplicating the real init service. Host-only decoder
controls are simpler but cannot prove native bootstrap rejection/no I/O/cleanup.
No normal runtime complexity is added; legacy evidence/profile defaults stay valid.
Owner/payload/kernel boundaries follow the already reconciled v2 contract. Record
remaining malformed/stale/foreign/wait and useful-shell work rather than claiming
SUSTAIN-01–06 or SI-07/R1 completion. No sibling repository/chat changes.

## Result and bounds

Both child mismatch directions pass natively: parent and owner remain matched,
bytecount exits120/kind1 with no submitted child frame/I/O progress, its stream is
EOF, and backend stdout/stderr stay empty. The observer confirms runner stop143/
kind3, retires client endpoints/tasks, closes backend handles, observes backend17,
reclaims it, verifies stale denial and obtains halt with three reclaims. Runner
stop and backend byte assertions are inside the inspected owner; UART exposes
child120/backend17, proof marker and final reclaim count. This is not an additional
independent backend-byte channel or general production recovery implementation.
Both matched one-cycle controls pass exact `6\n`, statuses0/0/17, three reclaims and
halt. All four retain actual idle beyond3000 ticks. No normal source is modified.

Maximum linked code is9736/16384 and scoped estimated stack3784/4088. The inspection
conservatively includes present memcpy/memset/memcmp targets at indirect calls;
immutable GOT decoding and manual register call-site inspection are retained. It
is not formal all-path/kernel-stack assurance. Raw images equal ELF binary extraction.
All compiler/native attempts passed on first execution; existing compiler warnings
remain in logs. `native-comparison.json` records strict comparisons and deliberate
trace corruptions; generic failure, wrong terminal/generation/reclaim, extra workers
or missing/late proof cannot pass.

The matched parent/child ELFs and backend/startup are exact pinned members of the
prior sealed SI-07 packet. inputs/ records that seal, the client profile and musl
notice. Per-case production hashes and copied/mutated sources remain frozen through
build/run; mutations.json identifies test-only changes. Fixed48-byte experiment
entropy makes no production entropy claim. All work uses unchanged AENSI001/ABI22,
current kernel, original limits and owner-held capabilities. No sibling or released
standard bytes, actual sys-init owner or public CLI behavior are changed.

This adds native child-bootstrap mismatch coverage to the bounded SUSTAIN-03
checkpoint; remaining malformed/stale/foreign schedules, wider wait-transition
coverage, useful shell integration and full SI-07/SDK/reader/R1 acceptance remain
open. No blanket external blocker is established for continuing bounded work.

## Reproduction and retention

From the repository root, with the pinned tools:

```sh
python3 docs/evidence/si07-child-profile-2026-10-03/build.py v2-v1
python3 docs/evidence/si07-child-profile-2026-10-03/run.py v2-v1
python3 docs/evidence/si07-child-profile-2026-10-03/audit.py
python3 docs/evidence/si07-child-profile-2026-10-03/check-native.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Repeat build/run for v1-v2, v2-v2 and v1-v1. Builds and run attempt labels reject
reuse. Audit.py requires all four built roots and also rejects existing output.
After cleanup, restore indexed artifacts and source exports first or select a new
unique dated attempt. artifacts.tar.gz retains generated outputs; every member is
hashed and read back before redundant owned build roots are removed. Per-case
source archives, mutations, command/native logs, compiler outputs and inspection
records remain directly readable. checks.json and SHA256SUMS bind the final packet.
