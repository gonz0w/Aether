# Native conflict guard consumer evidence

2026-09-06; decision 0091.

Decision 0091 accepts the bounded native synthetic conflict guard under the
explicit ABI-15 profile. All 156 cases pass: the 151 prior cases plus two guard
positives and three omission controls. Guard-conflict retains exact primary and
diagnostic histories; guard-resources preserves reader, worker, pending state,
token, generation and acquisition/launch counters while admission is closed.
Both positives complete at 100/3. Primary overwrite, skipped Driver closure and
forgotten reader reject exactly at 1052/0, 1053/0 and 1054/0, respectively.

The guard exclusively borrows Driver and both sample stores, reserving diagnostic
storage before the explicitly synthetic producer. Conflict closes Driver admission
without dropping owned resources. Explicit fixture cleanup and two subsequent
ordinary generations complete successfully. This is not a second kernel-produced
observation or a general diagnostic-producer API. Largest image is 4528 bytes;
the native workload now consumes an image beyond the old 4096-byte bound. The
extension contains read-only data/GOT entries; do not infer second-page instruction
execution from size. Producer page-permission and second-page execution evidence
remain separately pinned in decision 0090.

All 151 default ABI-6 images rebuild byte-for-byte identically. No producer,
linker bound, native operation, standards pin or sibling source changed. The
SI-05 compatibility refresh and its five requested guard cases now have consumer
witnesses. Next BG-058: qualify denied guard construction returning both original
borrows unchanged, and a dedicated control proving closed reoffer cannot invoke
the synthetic producer. The current repeated call returns Closed but is not that
omission qualification. PH-05 two-primary/one-diagnostic physical capacity,
PH-06 sealing, BG-057 PH-07 retirement and BG-033 recovery remain open.

`preflight/` retains the five strict builds and linker maps using decision 0088's
r7-aaa source layout. `source-review.json` records that identity and scoped review.
`legacy-build/` retains 151 identical ABI-6 rebuilds. `witness/` retains the full
fresh 156-case target run, exact source/producer/worker identities, commands and
raw supervisor/envelope/serial/QEMU artifacts. Its manifest is separately pinned
in the native catalog. ISO identities are retained in results; private ISO outputs
are not archived. `prior-image-comparison.json` compares the earlier ABI-15 bytes.
`validation/` and `adoption/` retain full local checks and final records. The root
manifest seals this new bundle. No historical or vendored evidence was rewritten.

Validation: all nine development gates pass in `out/checks/run-7opon4qp`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the fresh target snapshot. Offline native audit covers 2516
historical outcomes across 47 bundles; all 42 harness tests and nine host wrapper
cases pass. Full validation and adoption records are retained under
`docs/evidence/native-conflict-guard-consumer-2026-09-06/`.
