# Native history sealing evidence

2026-09-06; decision 0094.

Decision 0094 qualifies owned-history replay denial for Live, one/two-return
Awaiting, malformed-status Failed, and Interrupted after one/two returns. The six
positives complete at 100/3. False acceptance, erased primary and forgotten reader
controls reject exactly at 1061/0, 1062/0 and 1063/0. Repeated replay/conflict/capture
denials preserve complete samples, original binding/resources, issuance, generation,
pending/closed state and counters. No synthetic conflict producer runs. Explicit
fixture disposal preserves history and consumed issuance; it does not qualify
retirement. The malformed status slot and local interruptions are explicitly
synthetic; other retained returns come from the pinned native producer.

All 175 native cases pass (166 prior plus nine). All 151 ABI-6 images rebuild
identically. No new allocation, unsafe code, syscall, producer/worker source,
standard pin or sibling change. Next BG-058 PH-06: native errno history under this
owner, plus closed terminal inspection/replay without reset; BG-057 PH-07 whole-cut
retirement and BG-033 recovery remain separate. This slice establishes the six
listed source dispositions, not all failure combinations or production init.

`preflight/` retains all nine initial strict links and their source before the
reviewed cleanup/final-oracle refinements. `witness/` retains final consumer,
producer and worker pins, raw supervisors/envelopes, serial/QEMU logs and complete
175-case results. ISO hashes are recorded; private generated ISOs are not archived.
`legacy-build/` retains the 151 identical ABI-6 rebuilds (build-only compatibility).
`consumer-review.json` records tool/input identity and prior-image comparison.
`validation/` and `adoption/` retain final checks and records; root `sha256.json`
seals the bundle independently of the catalog-pinned witness manifest. Existing
sealed evidence and sibling sources are unchanged.

Prior-image review: 162 of 166 ABI-15 images are identical. The four capacity
images keep their sizes; their only changed bytes encode line numbers shifted
by the new 16-line method at unchanged unwrap sites, consistent with panic-location
metadata. Exact offsets and source correspondence are retained in
`prior-image-differences.json` in the evidence root. All four freshly pass.

All nine repository gates pass in `out/checks/run-hti9fxbz`, with unchanged checked inputs. The offline audit verifies 3,019 recorded native outcomes across 50 bundles; the new 175 cases also have fresh QEMU execution. Final logs and adoption records are retained under `docs/evidence/native-history-sealing-2026-09-06/`.
