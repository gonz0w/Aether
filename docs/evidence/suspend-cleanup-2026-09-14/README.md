# Native suspend lifecycle cleanup

The existing copied-process fixture now exercises stopped suspension, ignored or
blocked child notifications, and repeated stop after child exit. The prospective
[review](../../NATIVE-SHELL-STARTUP.md#suspend-lifecycle-cleanup-review--2026-09-14)
records authority, resource bounds, forbidden outcomes and test selection.
Only the fixture and harness change; kernel implementation, ABI, released pins
and sibling repositories are unchanged.

- Stop: observe parent parked while the child is live; stop parent, require
  query144/kind3 (retained status143), clear parked state and repeat stop. Complete
  child I/O; its subsequent exit cannot resume the terminal parent. Require EOF
  on the parent's request channel before reclaim, then reject its retired query
  and stop handles. Repeat in fresh generation2, six total reclaims.
- Ignore/block: install SIG_IGN or keep SIGCHLD in the temporary suspension mask.
  Observe parking, complete child72, yield/check continued parking 16 times,
  then stop and apply the same cleanup checks. This is bounded schedule evidence,
  not a time-based liveness claim or an eventual unblock/delivery test.
- Repeat: normal child72 wakes its parent once. Receive and hold the parent's
  first invalid-selector wait request, proving it returned from its handler.
  Stop the terminal child twice and require unchanged72/kind1; release ECHILD.
  The parent retains its handler, explicitly polls and requires count1, then
  restores the old action and finishes all existing wait checks. Parent71,
  backend17 and six reclaims across two generations qualify.
- Controls: skipping the first stop must reject owner2331 with no terminals or
  reclaims. An extra self-post after the repeated-stop reply must reject raw
  parent236/owner1950 with child72 retained and no reclaims. The latter catches
  an oracle that restores DFL too early and silently discards duplicate posts.

Supervisor stop does not emit a `NATIVE terminal` serial line. Its status and
cleared parking are asserted by the owner; successful stop/ignore/block serial
inventories contain child72/backend17 twice. Normal exit still has its existing
serial contract. No presentation or diagnostic kernel behavior was added.

## Attempts

Focus1 reached complete guest success for parked stop, but the harness incorrectly
expected a serial terminal line for supervisor stop. Correcting that oracle keeps
the retained-status and parked-state checks intact. The remaining cases had not
run. Focus2 failed before any target build: an interrupted edit left the focused
selector's count at ten after an eleventh control was registered. The exact
snapshot and selector failure are retained; this is tooling failure, not a guest
result. Focus3 passed stop/ignore/block and reached parent71 in repeated-stop, but
the owner waited for six further requests after already servicing the first one.
Selecting five remaining requests for that profile fixes the fixture. Focus4
passes all eleven focused profiles, including the unchanged dash wait and its
disabled-route control. No kernel change was used to bypass any failure.

Host-final2 belongs to the final source revision. Earlier host and host-final
results belong to attempts1 and3, respectively. Each revision and failed attempt
is preserved. All 312 connections cases pass in 971.43s on 265 frozen inputs, along with
all eleven focused cases and 101 host Python tests plus Zig/offline checks. Scoped
format checks pass. qualification.json and cleanup-traces.json record the results.

## Remaining scope

Stale-parent replacement before the old child's exit still needs its own native
rendezvous. Bad-handler recovery, default termination during suspension and nested
delivery remain gaps. Ignored/blocked tests end in stop; eventual unblocking is
not claimed. Matching command-runner evidence and independent consumer/SDK review
remain required before acceptance. This is not an interactive boot image or R1.
The preceding seven scheduler regressions are referenced against unchanged kernel
sources, not represented as freshly executed here.

Compatibility: 894/894 compared pre-existing client,
owner and kernel artifacts are byte-identical; compatibility.json lists every
changed artifact. This does not imply independent consumer acceptance. All four
newly generated unpacked target directories were removed only after every file
matched its preserved archive. Failed attempts remain in those archives; the
pre-build selector failure has its own log and source snapshot. Exact paths and
sizes are recorded in duplicate-cleanup.json. No other build directory was removed.
SHA256SUMS seals all packet members.
