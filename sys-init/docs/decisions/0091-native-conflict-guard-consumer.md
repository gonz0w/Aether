# 0091 — Native conflict guard consumer

Plan, 2026-09-06; BG-058 following decision 0090.

Integrate the retained decision-0088 r7-aaa guard layout into the explicit ABI-15
fixture. Pending exclusively borrows Driver and both sample stores, reserves the
empty diagnostic store before synthetic production, retains primary and conflicting
histories and propagates Conflict to Driver.closed. No native operation or unsafe
boundary is added. The candidate producer is explicitly synthetic, not independent
kernel evidence. Held retains a diagnostic sample only after complete identity
validation; its shared origin remains associated with the primary View.

Run guard-conflict and guard-resources to exact 100/3 completion. Primary overwrite,
skipped Driver closure and forgotten reader must reject exactly at 1052/0, 1053/0
and 1054/0 respectively. Run all 151 prior ABI-15 cases on the same frozen source
and producer. Add guard cases only to --init-large; preserve the default ABI-6
fixture bound and verify prior images by byte comparison. Run existing host Held
identity/history and omission tests plus all nine development gates. Retain every
attempt and source/tool identity. No failed link, timeout or boot error counts as
semantic rejection. No sibling source, producer pin or released standard changes.

This qualifies the bounded synthetic conflict path, not construction-denial
ownership return, producer non-invocation on closed reoffer, physical nine-triple
capacity, sealing or retirement. Track those follow-ons in BG-058/BG-057 before
completion. Shared O/I/E authority and evidence obligations remain unchanged;
Distribution budgets and production conformance are not inferred from image size.

## Results and remaining scope

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

All 151 of 151 prior ABI-15 images also remain byte-identical; every case still
has fresh target execution on this source set. The first complete run passes,
with 472 successful commands and 421 frozen inputs unchanged. All five strict
preflight links and the existing nine host wrapper tests pass. No runtime retry
or weakened oracle was needed.

Validation: all nine development gates pass in `out/checks/run-7opon4qp`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the fresh target snapshot. Offline native audit covers 2516
historical outcomes across 47 bundles; all 42 harness tests and nine host wrapper
cases pass. Full validation and adoption records are retained under
`docs/evidence/native-conflict-guard-consumer-2026-09-06/`.
