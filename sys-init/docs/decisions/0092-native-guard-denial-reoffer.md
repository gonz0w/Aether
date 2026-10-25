# 0092 — Native guard denial and reoffer

Plan, 2026-09-06; BG-058 following decision 0091.

Qualify Pending::begin denial for an unsealed primary and an occupied diagnostic
store. Require the exact original Driver, primary and spare addresses, complete
sample equality and retained reader/worker/token/pending/generation/counters. The
unsealed case must subsequently read and construct a guard using the returned
borrows; the occupied store must remain unchanged through denial and cleanup.
Controls that forget the reader or clear the spare must reject at 1055/0 and
1056/0. Positives complete at 100/3 after explicit cleanup and ordinary reuse.

Instrument the private synthetic producer entry with a bounded caller-owned
counter. A first conflict invokes it once; a closed reoffer must not invoke it,
change either history or reopen ownership. A deliberate bypass of both admission
checks must reach that same producer closure and reject at 1057/0. The counter
is fixture observability, not a production metrics/API feature. No allocation,
unsafe block, syscall, authority or producer/standards pin is added.

Run six new cases and all 156 prior ABI-15 cases on frozen inputs. Run existing
host conflict/omission tests, verify the 151 ABI-6 image bytes and run all nine
local gates. Preserve all failures and exact native oracles. Track remaining
PH-05 two-primary/one-diagnostic capacity, PH-06 sealing and PH-07 retirement;
these six cases do not establish them or all invalid constructor combinations.

## Results and remaining scope

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

All 162 cases pass on the first complete run: 490 commands, 421 frozen inputs
unchanged, maximum image 5072 bytes within 8192. 156 of 156 prior ABI-15
images remain identical; every case has fresh execution. All six preflight links,
nine host wrapper cases and 42 harness tests pass. No failed runtime attempt or
weakened assertion was needed.

Validation: all nine development gates pass in `out/checks/run-kym_6_tc`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the target snapshot. Offline native audit covers 2678 historical
outcomes across 48 bundles; nine host wrapper cases and 42 harness tests pass.
Full validation and final adoption records are retained under
`docs/evidence/native-guard-denial-reoffer-2026-09-06/`.
