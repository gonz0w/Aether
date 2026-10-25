# Native stale-parent notification isolation

The [prospective review](../../NATIVE-SHELL-STARTUP.md#stale-parent-replacement-review--2026-09-14)
adds a pre-bootstrap rendezvous to the existing two-generation fork/suspend fixture.
No kernel implementation, ABI, authority, quota, released pin or sibling changes.

After parent1 is observed parked, the owner stops it, checks cleared parking and
request-channel EOF, and reclaims it. It launches parent2 in the same slot while
child1 is still live. Parent2 installs public libc SIGCHLD handling and blocks the
signal before sending op86/generation2 with a zero tail on its own granted channel.
The owner validates readiness, old-parent query/stop handle rejection, a live
replacement and a still-live child1 before permitting old-child completion.

Child1 exits72 and backend1 exits17. After those two reclaims (three total), the
owner sends op87. Parent2 validates every field, unblocks SIGCHLD, explicitly polls,
and requires zero handler calls. It restores its prior disposition and empty mask,
then acknowledges op88. The owner retains this Connection into iteration2. Normal
bootstrap/fork/wait then requires child2 to wake parent2 once, parent71/backend17,
and six total reclaims. Thus both isolation from old provenance and successful
notification of the new parent are exercised, without extra dummy launches.

The negative control injects a self-post while SIGCHLD is still blocked, after
op87. Unblocking/polling must detect it and exit raw237; owner1950 with exactly
three prior reclaims is required. A failure before replacement readiness cannot
satisfy that oracle. The handler stays installed until after the zero-delivery
check, so resetting to DFL cannot hide an incorrectly queued notification.

## Attempts and qualification

Focus1 rejected replacement237/owner1950 after one reclaim, before readiness:
the fixture's sigprocmask facade correctly requires descriptor startup. The
pre-bootstrap probe now uses the existing raw size8 mask operation, preserving
the facade's gate. Public libc sigaction remains in use. No startup-ready flag
is forged. The failed source revision and all target artifacts are retained.

Focus2 passes all thirteen suspend-family/unchanged-dash cases. Host-final passes
101 Python tests plus Zig/offline checks on the final revision. The earlier host
run belongs to attempt1. All 314 connections cases pass in 979.07s on 265 frozen inputs.
All thirteen focused cases pass; qualification.json and cleanup-traces.json
record exact lifecycle and rejection results. Artifact archives are read-back
verified against their per-file hashes. Scoped C/Rust formatting passes.

## Limits

This is producer coverage, not independent userland/SDK adoption or a released
shell image. Failed suspend-frame recovery, default termination during suspension,
nested delivery, eventual unblock after a blocked post, matching command-runner
qualification and consumer review remain open. Kernel/scheduler sources are
unchanged; prior scheduler results are identified as prior evidence, not rerun.

Compatibility: 912/912 compared pre-existing client,
owner and kernel artifacts are byte-identical; compatibility.json lists every
changed artifact. This does not imply independent consumer acceptance. All three
newly generated unpacked target directories were removed only after every file
matched its preserved archive. Failed attempts remain in those archives; the
failed setup revision has its own log and source snapshot. Exact paths and
sizes are recorded in duplicate-cleanup.json. No other build directory was removed.
SHA256SUMS seals all packet members.
