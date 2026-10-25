# Unchanged dash redirection qualification — 2026-09-15

The unchanged userland `redirection.sh` writes A/B through duplicated file
descriptors, closes the writer, then runs the actual helper with a reopened file
on stdin. Exact stdout is AB. Helper0, dash0 and backend17 repeat twice with six
reclaims. This is producer evidence for volatile scratch storage, not persistence,
a completed consumer handoff or release readiness.

## Contract and scope

The existing capability-scoped file owner and dispatcher now accept the parent's
readonly reopen. Exact frozen fork/exec snapshots require FD0 on the reader and
FD10/FD11 on old stdin with CLOEXEC. Successful replacement removes those aliases
and releases only the child's old stdin holder; parent authority and the reader
survive. Admission and image preparation still precede publication/release.
The positive owner is 14,184 bytes, within the existing four-page bound.

The [shell contract](../../NATIVE-SHELL-STARTUP.md#unchanged-scratch-redirection-workload--2026-09-15)
records requirements, forbidden outcomes, affected owner/profile, standards and
test selection. O-02–04, I-01/05/06, E-01–06 and SE-01–05 apply. The simpler
existing owner/alias/restore path suffices; no extra descriptor store, service or
VFS abstraction is needed. The mistaken child-open path was removed after native
inspection. No new dependency, FFI boundary, kernel primitive, quota, sibling edit
or released standards pin change. New branches are restricted to the redirection
selection; 671 previous ELF/raw images are byte-identical (`compatibility.json`).
The existing workflow group and interface references document the new selections.

## Qualification

- `connections.json` and `connections-results.json`: all 352 cases pass in
  1091.437147 seconds, below the 1800-second review ceiling. All 264 runtime/support
  inputs remained frozen. Existing per-build/QEMU bounds are unchanged.
- `connections-traces.json` and copied serial logs: exact positive lifecycle above;
  dropping B or skipping the helper rejects child0/owner2310; retaining old stdin
  rejects child0/parent0/owner2131. Every control reports zero reclaims.
- `host-final.log`: all 104 Python tests and required Zig host checks pass.
- `checks.json`: Rust formatting, workflow, standards and four simplicity snapshot
  hashes pass. `final-checks.json` records checks after documentation updates.

Run from the repository root with the pinned native SDK and tools:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

`attempt-7-sources.tar.gz` is the final native source archive, mapped by
`final-sources.json`. Earlier attempt archives each retain their own exact input
map. The full native report records tool/SDK identity; replay requires those
external pinned prerequisites. `review-inputs.tar.gz` preserves final local review
and host-support inputs separately. The preserved selector and driver scripts
record focused/full invocation mechanics and original workspace paths.

## Retained investigation

Attempts 1–3 reject owner2506, owner2550 and diagnostic2601 respectively: the
initial assumption that the reader opened in the child was wrong; the parent
opens readonly before fork. Attempt4 deliberately emits a packed fork snapshot.
Attempt5 rejects owner2120 because the proposed exec table omitted FD11.
Attempt6 deliberately emits the exec snapshot. Both diagnostics decode identically:
FD0 binding3, FD1/2 standard streams, FD10/11 binding0+CLOEXEC, other encoded slots
empty (`snapshot-diagnostics.json`). Final validation checks all 16 slots;
diagnostic encoding covered the first 12 only. Attempt7 passes the positive and
three semantic controls. All failed/diagnostic outputs and source snapshots are
retained; temporary diagnostic code is absent from final sources.

## Preservation and remaining work

`focused-artifacts.json` records seven focused archives and verified duplicate
removal. `connections-artifacts.json` maps all 6,232 full-run artifacts preserved
in `connections-artifacts.tar.gz`. `connections-cleanup.json` records verification
against both archived members and originals before removal of the generated
full-run directory (3,972,389,997 bytes). Prior sealed evidence is unchanged.
`SHA256SUMS` seals this packet after collection and final checks.

Next is unchanged denied-redirection against the read-only input namespace.
Remaining consumer workload reconciliation, a matching command-runner run and
independent SDK/userland acceptance precede handoff. Poisoned-close recovery,
persistent filesystem/OpenZFS work and R1 assembly remain open.
