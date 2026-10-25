# Unchanged dash denied redirection — 2026-09-15

The unchanged consumer script attempts a write to /inputs/denied in a real
subshell, waits for its failure, then prints exactly `denied ok` plus newline.
The existing scratch backend enforces EACCES. The dispatcher now supports the
empty file grant and fork-issued stream references for this non-exec child.
No authority is gained from a pathname or copied numeric handle.

## Scope and review

The [native shell contract](../../NATIVE-SHELL-STARTUP.md#unchanged-denied-redirection--2026-09-15)
records the requirement, forbidden effects, owner boundary, standards clauses and
preimplementation test selection. Aether owns this private producer adapter;
userland owns independent intake and the supported SDK boundary. O-02–04,
I-01/05/06, E-01–06 and SE-01–05 apply. Reuse the existing backend denial and owner:
a new namespace service or kernel mechanism is unnecessary. Fork/exec legacy
paths remain for their existing consumers. No dependency, new unsafe boundary,
quota, sibling edit, released pin or backend change. This is volatile scratch
coverage, not persistent filesystem or full-dash acceptance.

The child's authenticated root reaches the existing gateway. Exactly one denied
open must return EACCES with no handle, leave file ownership closed and unpoisoned,
and precede child stream requests. Successful completion requires no exec,
nonempty stderr, exact backend stdout readback, observed child2/parent0/backend17,
wait collection and closed stream holders. Two generations reclaim six tasks.
Unchanged upstream dash diagnostics remain within the existing experience
exception; no machine markers or user output are restyled.

## Results and reproducibility

Focused positive, wrong-errno and dropped-stdout cases pass (`focus-3.log`).
The wrong-errno control changes the actual backend response to ENOENT and must
reject owner2554 before the client receives it. The dropped-output control lets
the parent believe its write succeeded; independent readback rejects
child2/owner2310. Both controls require zero reclaims.

`host-attempt-3.log` records all 104 Python tests and required Zig checks passing
on the final source set. `checks.json` records formatting, workflow, standards,
whitespace and four simplicity input hashes. Full native qualification passes: `connections.json` and `connections-results.json`
record all 355 cases in 1105.852922 seconds, below the 1800-second review ceiling,
on unchanged sources. `connections-traces.json` verifies exact positive and
control lifecycle lines. `final-checks.json` records final documentation checks.

`attempt-3-sources.tar.gz` and `final-sources.json` preserve the final 266
runtime/support inputs. Each previous attempt has its own verified source archive.
`connections-results.json` records native SDK/tool identities. Replay requires the
pinned external SDK/tool prerequisites; the source archive alone is insufficient.

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

The preserved focused selector and full driver record exact invocation mechanics
and original workspace paths. The existing AT-CONNECTIONS workflow group includes
the new cases. `review-inputs.tar.gz` preserves final local review/support inputs.

## Retained failures and compatibility

Attempt1 stopped before native execution: a misplaced lifecycle-check insertion
caused a Python indentation error. Its log and source archive remain. Attempt2
reached child226/owner2130: the owner expected replacement stream references from
a child that had never executed a replacement. Attempt3 uses the child's existing
fork-issued references and passes all three focused cases. This corrects the
adapter's expectation without broadening authority or altering the backend.

`compatibility.json` compares 679 prior ELF/raw images: 671 are byte-identical.
Eight scratch-owner binaries grew 32–48 bytes; all remain within four pages and
are included in the full regression suite. Existing client images are unchanged.
Do not claim byte identity for the eight changed owners.

`focused-artifacts.json` records both native attempts, exact archive member hashes
and verified removal of their duplicate generated roots. The pre-native failure
has no native output root. Full artifacts, traces and cleanup receipt are retained
separately; archive verification must precede duplicate removal. Prior sealed
packets remain unchanged.

## Remaining work

Reconcile the unchanged consumer substitution, multi-stage pipeline and early-reader
workloads with the existing bounded pipe experiments; their exact consumer
acceptance is still missing. Match the command-runner suite on the final handoff
sources and obtain independent SDK/userland acceptance. Poisoned-close recovery,
persistence/OpenZFS, package execution and sys-init R1 assembly remain open.

Final preservation: all 6,283 full-run artifacts were verified against
archived members and original files before removing their generated directory.
Together with the focused runs, 4,491,858,403 bytes of verified duplicate output
were removed. `SHA256SUMS` seals this packet after final checks.
