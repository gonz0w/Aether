# Native guard denial and reoffer evidence

2026-09-06; decision 0092.

Decision 0092 passes all 162 native cases: 156 prior cases and six new denial/
reoffer probes. Unsealed-primary and occupied-diagnostic construction denials
return the original Driver, primary and spare addresses with both full sample
values and the checked ownership/counter fields unchanged. The unsealed case
then reads and constructs a guard using those returned borrows. The occupied
store remains unchanged through explicit cleanup. Both complete at 100/3;
forgetting the reader rejects at 1055/0, and clearing the spare rejects at 1056/0.

A caller-owned bounded counter observes entry into the actual private synthetic
producer closure before spare acquisition. The first conflict invokes it once;
the closed reoffer returns Closed without increasing the count or changing either
history. Bypassing both Driver and Held admission checks reaches that same closure
again, even with no spare available, and rejects exactly at 1057/0. The positive
finishes at 100/3. This is fixture observability, not a metrics or public producer
API. The two snapshots used by the denial oracle are test data, not proof of the
future physical nine-triple storage limit.

All 151 ABI-6 images rebuild byte-identically. No syscall, unsafe block, heap
allocation, producer/standards pin, ABI bound or sibling source changes. Next
BG-058: PH-05 two primary histories with one reserved diagnostic store under the
shared Driver owner, then PH-06 sealing. BG-057 PH-07 retirement and BG-033 recovery
remain open. This slice does not cover every invalid constructor combination or
retention after guard destruction, and does not establish the full storage budget.

`preflight/` retains six strict builds, maps and source snapshots. `legacy-build/`
retains all 151 byte-identical ABI-6 builds. `witness/` retains all 162 native
outcomes, exact commands, frozen consumer/producer/worker inputs, supervisors,
envelopes, serial and QEMU logs. Its separate manifest is pinned by the native
catalog. ISO identities remain in results; private ISO outputs are not archived.
`prior-image-comparison.json` records prior ABI-15 build equivalence, not a
substitute for the fresh execution. `validation/` and `adoption/` retain checks
and final records. The root manifest seals this new bundle; historical evidence,
released bytes and sibling sources are unchanged.

Validation: all nine development gates pass in `out/checks/run-kym_6_tc`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the target snapshot. Offline native audit covers 2678 historical
outcomes across 48 bundles; nine host wrapper cases and 42 harness tests pass.
Full validation and final adoption records are retained under
`docs/evidence/native-guard-denial-reoffer-2026-09-06/`.
