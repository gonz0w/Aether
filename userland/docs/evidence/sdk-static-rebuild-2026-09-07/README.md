# SDK-07 local static input/relink evidence

The corrected SDK-05 run sdk-startup-lefmmlgo was reviewed: current source hashes
match its recorded inputs, all receipt_sources match the selected SDK receipt,
and all 13 process receipts are complete. No label key is required: its commands
are process records with argv. The earlier source-selection finding is resolved.

The new experiment repeats the receipt-pinned imported-SDK startup/denial suite,
then adds an unused member to a private copy of libc.a. Baseline link-input hashes
now identify exactly one changed input; the old binding is stale. An input binding
containing only the unchanged probe object remains equal. An artifact-only check
misses the change because the old ELF has not changed.

A real relink and ELF/no-extra-undefined checks pass. The new ELF is byte-identical:
the extra archive member was unused. Fresh input and artifact receipts nevertheless
record a different archive hash. Both baseline/candidate archive copies remain in
the build root; restoring the working archive restores the baseline fingerprint.
All 231 original imported SDK inputs are rechecked unchanged after the experiment.
No candidate package is admitted, and no ELF is executed.

| Attempt | Result |
| --- | --- |
| sdk-static-xktw9e00 | Incomplete: fixture looked up probe.o instead of receipt-pinned io_probe.o; KeyError after archive-add. Retained work/commands; no imported input changed |
| sdk-static-b2isn1mq | Pass: 18 complete owned command receipts, changed archive detected, relink/ELF checks pass, imported SDK unchanged |

Source/plan/tool/package hashes, exact commands/environment, raw streams and input
bindings are retained per attempt; binaries/archives remain in named build roots.
The captured one-shot driver extends the existing startup fixture; its inherited
PASS marker names startup linking, while summary.static_rebuild records this slice.
prepare-experiment.py documents the generation step and is not package machinery.

This establishes local static-link input invalidation and explicit relink/check
tracking. It does not implement pkg-mgr update selection, automatic reverse-consumer
rebuilds or prove a changed SDK remains native-compatible. The disjoint-input
control is a receipt comparison, not a second executable workload. Full package
SDK-07 integration remains separate. SDK-08 native execution is NOT RUN; source
trust and independent technical/reader review remain open. No sibling changed.
