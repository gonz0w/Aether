# Failed-exec native prototype

Implements the selected intake contract in NATIVE-SHELL-STARTUP.md. First probe: unchanged script, two actual child exits127/126, parent0/backend17 and four reclaims. No kernel quota or ABI change. Owner object bytes are the immutable `Aether non-executable fixture\n` constant with no image grant. Source snapshots pin that object; it is not a filesystem mount or POSIX mode-based grant.

Attempt logs and source snapshots are preserved before fixes. The first focus run is a prototype, not full-suite or consumer acceptance. Those checks are completed in the qualification below. Existing matched qualification remains sealed and applies only to its prior source set.

## Qualified result

The unchanged script now passes in two fresh native VM runs on the same final
sources: the focused six-case run and the complete connections run. Each positive
requires child127 generation1, child126 generation2, parent0 and backend17, exact
owner stdout readback `exec errors ok\n`, and four reclaims. The child slot is
reused within each run; two script lifetimes in one VM remain unqualified.

All 322 connections and 431 command-runner cases pass on matching 267 frozen
sources, strict SDK and tools. Host tests pass. Seven scheduler regressions passed
after the kernel verdict change; only fixture/harness controls changed afterward,
as recorded in scheduler-coverage.json. This is producer evidence, not independent
consumer acceptance, stock SDK installation, a general filesystem or full POSIX.

Five deliberate controls pass their exact rejection checks: missing-as-denied
child126/owner2130 with zero reclaims; denied-as-missing second child127/owner2130
with one reclaim; skipped second owner request second child226/owner2130 with one
reclaim; false successful stdout write owner2310 after both children/two reclaims;
retained first child owner2153 with zero reclaims. Full native-traces.json checks
both focused and complete-suite outcomes independently of the harness pass flag.

The explicit native-exec-denial flag changes the fixture completion verdict only:
four reclaims plus exact slot generations1/1/2, with all normal empty-domain/channel
checks retained. It requires the existing copy/exec/local-runner/single-context
signal-copy settings. Disabling it rejects the otherwise successful four-reclaim
trace under the previous six-reclaim verdict; missing prerequisites also reject.
No kernel operation, authority or generation quota was extended.

## Retained failures

Attempt1 rejected owner2340 during request validation. The original environment
comparison assumed ordering not required by the consumer contract. Attempt2 used
exact unordered entries and reached child226/owner2130: denied exec retains copied
0x77000000-based references, not the replacement's 0x76000000-based references.
The scoped dispatcher correction preserves that distinction without accepting both.
Attempt3 reached the entire expected127/126/0/17 trace and four reclaims, then the
old kernel completion verdict rejected. Attempt4 and the first host run failed to
build because the new option referenced a variable declared later. Moving its
prerequisite check after those declarations fixed it. Attempt5 then passed; final
control additions were frozen for attempt6 and both full suites. No failure was
relabelled as a positive result. The first four focus logs have filesystem timestamps
and harness commands rather than outer process start/end receipts; later runs have
explicit receipts. The per-case watchdogs remained in force.

## Consumer intake and remaining work

Use attempt-6-sources.json and attempt-6-sources.tar.gz as the final source set;
all earlier attempt snapshots are historical. The existing sealed suspend-runner
support/SDK intake remains reference setup, but its progress documentation predates
this work. Apply this packet's documentation snapshot after restoring support and
final sources; verify all hashes before replay. Run the existing --connections
and --command-runner commands sequentially with the pinned SDK/tools, selecting
3600-second outer deadlines and reporting elapsed time against the 1800-second
review ceiling. This turn did not qualify a fresh restored consumer checkout.

Userland must independently consume the new failed-exec script/control set and
review the public SDK boundary. Next kernel-owned work is the writable descriptor/
redirection path needed by fd-leak-control and the remaining unchanged workloads.
Default/nested signal behavior, general paths/TTY, persistence, OpenZFS, package and
sys-init assembly remain separate R1 gates. Siblings and released pins are unchanged.

Compatibility: all 608 compared pre-existing client/owner ELF and raw images are
byte-identical; the 316 changed artifacts in compatibility.json are kernels. Both
complete suites finished within the 1800-second review ceiling (see timing-review.json).
