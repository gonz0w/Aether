# Independent dash recovery acceptance — 2026-09-29

**RECOVERY-01–06 accepted for private AENMX007/ABI21 scripted execution.**
Rebuilt and replayed the unchanged consumer script in three native dash parents.
All128 capacity cases, five non-pipeline command cases,119 Python tests and the
configured Zig/Rust host checks pass. Seven independent consumer comparisons and
36 rejection controls pass. No native attempt failed or needed rerunning.

The shell recovers after a real early reader exits: pump sees EPIPE and exits42,
then the same parent runs argv/environment verification and a fresh healthy
three-stage pipeline, checks closed descriptors, and exits0. Per parent, stdout
is exactly49 bytes and stderr20. Across three parents:21 copies,18 helper exec
replacements,21 image admissions and24 checked terminal/reclaim results. Exact
identities, phase order and separate streams are bound in recovery-checks.json.

Native negatives exercise wrong EPIPE, wrong environment, an inherited descriptor,
a real retained reader requiring confirmed stop/cleanup, stale collected-child
wait and corrupted healthy output. The bad-byte case completes cleanup but fails
the ordinary stream oracle. Consumer counterexamples additionally reject wrong
admission, duplicate/early observation and duplicate/missing terminal records.
No watchdog timeout or generic crash is treated as semantic rejection.

## Inputs and reproducibility

Producer: recovery-native-2026-09-25, manifest SHA256
`a3eb4dda526803eaa665feb8a2ab67f5aaab6e53ca8767c542428483a234b812`.
Verified its complete seal before consuming the export. Restored669 source/support
files, matched297 capacity runtime hashes and the separate legacy source inventory,
and verified4311 SDK files before and after execution. Tool pins and clean process
environment are recorded in preparation.json, run.py and process receipts. No
sibling implementation was edited and no mutable sibling source was built directly.

The export omitted the historical driver/frozen inputs for its five requested
legacy cases. The explicit21-file legacy-supplement restores those from the earlier
manifest: driver hash is fixed in supplement.py; the input manifest matches the
final producer legacy receipt. This is a documented supplementary dependency,
not a claim that the original export was complete. No runtime bytes were replaced.
See source-review.md and legacy-supplement.json.

Owned execution:3600-second native deadlines,1800-second review ceilings,
512MiB streams, unchanged guest watchdogs; host300 seconds. Actual elapsed times:
capacity447.14 seconds, legacy17.13 seconds, host10.99 seconds. All outer owners
report complete process cleanup. These are run observations, not speed benchmarks.
Commands and intermediate receipts remain in run.py and *-timing/process records.
The source export and explicit supplement permit a fresh replay; use a new evidence
and build root, never overwrite this sealed packet.

All five locally rebuilt recovery owner raw hashes match the producer's reviewed
images: code fits24KiB; recorded maximum stack3688 of4088 bytes. stack-bindings.json
binds this reuse. It is scoped contributor assessment, not formal whole-program
proof or an independent human stack review. Raw case logs are under cases/.

## Scope and next action

Current acceptance: experiments/dash-native/RECOVERY-ACCEPTANCE.md. The original
SESSION-RECOVERY.md/script/manifest and all prior sealed evidence remain unchanged.
The full capacity selection covers the changed fixture completion path and prior
session cases; five regressions cover the unchanged non-pipeline branch. We do
not claim prior358-connection/431-runner tests were rerun on these bytes.

UL-007 remains active. Next consumer compositions are failed-exec recovery, scratch
redirection and real serial input. SI-07's generation-3 dependency still needs the
complete versioned bootstrap/decoder profile and rebuilt runner/bytecount. Shared
SDK, independent reader review, general TTY/POSIX support and full M3/R1 remain open.
Final source/tool/evidence verification, local quality and archive results are
recorded separately in this packet; archive retention is not runtime acceptance.

Final checks pass: local quality, Python syntax, whitespace, source/SDK/tool and
consumer input pins, and all four preceding evidence seals. Archive readback
verified both new suites before deleting their redundant directories; subsequent
archive/index hashes also match. Net reclaimed966,246,400 allocated bytes
(about921MiB), including the new build cache. Earlier builds/evidence were untouched.
No independent reviewer sign-off or minimum-Python-version execution was invented.
