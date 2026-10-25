# SI-07 composed wait schedules — 2026-10-03

Before-code requirement: qualify the unchanged ABI22 observe/park mechanism in a
matched v2 useful command. Two copied-owner fixtures check input wake, a second
level-ready wait before consuming the byte, a deadline after consumption, rejected
future sequence with unchanged observation, and owned lifecycle events retained
before registration after complete command cleanup. The delayed case additionally
requires at least10 guest ticks between empty read/snapshot and input wake; the
host withholds input for200ms after the real command prompt. Both perform one exact
6-newline/0/0/17 cycle, reclaim three and accept fresh authorized halt after >3000
idle ticks. Wake itself is never treated as a completed command. Generic failure,
timeout, early input or missing cleanup cannot qualify the selected schedule.

Owner/profile: kernel observe/park and serial grants remain supervisor-scoped;
userland pinned runner/bytecount transport and sys-init lifecycle policy remain
unchanged. Only copied Rust fixture sources gain assertions; no kernel hook,
service, shared state, dependency, unsafe boundary, quota or ABI is introduced.
Untrusted input is consumed exactly once; compare/park uses the existing IF=0
boundary and live synchronous trap buffers. The before-registration lifecycle
sequence can include terminal/channel/cleanup events; this is not an isolated
terminal-source proof. No arbitrary cancellation operation is invented.

Simplicity: compose existing operations around the real command rather than add
an event framework or expose address waits. Host-only core tests do not establish
native scheduler/serial composition. Added complexity is confined to the two
copied test owners and exact trace oracle; none is added to maintained runtime.
Earlier mechanism and protocol evidence remains immutable. This covers two bounded
schedules, not exhaustive race/cancel/framing coverage or sys-init acceptance.
Select frozen native runs, raw/ELF/stack/GOT inspection, semantic trace corruptions,
host/pin/workflow/Experience/link checks and verified artifact retention. Update
STATE/ROADMAP/current reference and retain every failed attempt. Foundations
O-01–05/I-01/03–06/E-01–08 and local SE-01–05 apply. Existing compressed recipe
style is inherited in copied support; no broad harness rewrite is mixed in.

## Result

Both level-2 and delayed pass in real QEMU. Before admitting any workers, input is
empty; one wake returns with unchanged event sequence, and a second wait observes
the same unconsumed serial readiness. Exactly one r is consumed. A future sequence
returns -22 without changing observation; the subsequent empty wait reaches its
absolute deadline with -110 and unchanged sequence. The delayed case additionally
asserts at least10 guest ticks elapsed before the first wake; the host schedule
records its measured200ms withholding. These are bounded schedules, not a formal
proof of all registration/input interleavings or a performance benchmark.

Each case then executes the unchanged matched runner/bytecount command, checks
exact6-newline and0/0/17, closes/reclaims all clients/backend and rejects stale
references. The lifecycle snapshot precedes backend closure/terminal/retirement;
waiting on that old sequence after cleanup returns the retained event and current
sequence. This includes channel/terminal/cleanup publication, not an isolated
terminal-source guarantee. The ordered proof precedes fresh halt input, three
reclaims and authorized halt; both retain >3000 actual idle ticks.

Two trace comparisons and28 semantic corruptions pass. Raw/linked code9912/16384
and estimated stack3784/4088 fit existing bounds. Raw/ELF equality, immutable GOT
and register provenance are inspected. Production source hashes stay unchanged.
Source-preparation level failed before compilation because a Python newline literal
did not match the Rust escaped newline; partial copied sources, initial recipe and
failure classification are retained. Corrected level-2 and delayed builds/runs pass
on their first compiler/native attempts. Existing fixture warnings remain in logs.

No kernel runtime, grants, quotas, sibling, standard pin or actual sys-init policy
changes. This covers composed input/retained-event/deadline behavior; arbitrary
cancellation, exhaustive races, truncated framing, consumer acceptance and full
SI-07 remain open. These gaps do not by themselves require another kernel API.
Next is explicit matching sys-init/serial-shell profile reconciliation before
wiring the already qualified shell to sustained lifecycle ownership. Shell,
persistence/packages and assembled R1 acceptance remain separate.

## Reproduce and retain

From the repository root, with pinned tools:

```sh
python3 docs/evidence/si07-wait-composition-2026-10-03/build.py level-2
python3 docs/evidence/si07-wait-composition-2026-10-03/run.py level-2
python3 docs/evidence/si07-wait-composition-2026-10-03/build.py delayed
python3 docs/evidence/si07-wait-composition-2026-10-03/run.py delayed
python3 docs/evidence/si07-wait-composition-2026-10-03/audit.py
python3 docs/evidence/si07-wait-composition-2026-10-03/check-native.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Build/run/audit reject existing attempts. Run uses a90-second external watchdog,
private firmware variables, bounded serial capture and explicit VM teardown;
start/end UTC and input timing are retained. Generated artifacts and copied source
archives receive full hash/member readback before retain.py removes only the three
owned duplicate roots (including the preparation failure). Restore indexed artifacts
and sources before replay after cleanup, or use a fresh dated attempt. checks.json,
source hashes, logs and SHA256SUMS bind the result. This does not publish a release.
