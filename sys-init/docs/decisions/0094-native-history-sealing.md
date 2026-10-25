# 0094 — Native history sealing

Accepted bounded experiment, 2026-09-06; BG-058 PH-06 after decision 0093.

Add a private replay entry on History using the existing Sampling terminal-view
factory and original retained binding. It performs no read, allocation or lifecycle
effect. Live, one/two-return Awaiting, malformed-status Failed and synthetic
Interrupted after one/two returns must deny terminal replay. Conflict requests
must deny (or return Closed for failed owners) without entering their producer.
Check whole Sample equality, the unused primary/diagnostic, exact reader/worker,
issuance, generation, pending, closed, fact/error and acquisition/launch/read counts
before and after repeated denials. Explicit known fixture cleanup remains separate
from retirement; histories survive disposal. No reset or acknowledgment API.

Six positive configurations finish at 100/3. Three controls at the replay denial
boundary falsely report Duplicate (1061/0), erase the sample (1062/0), or forget
its reader (1063/0). These are trusted local omission probes, not external attacks.
Malformed status is labelled synthetic and omits that native call; all other raw
returns are captured from the pinned target. Interruption is a local synthetic
disposition, not native syscall cancellation. Native errno variants and broader
closed terminal replay/retirement remain follow-on work unless qualified here.

Run strict ABI-15 links under unchanged 8192 bytes, all 175 native cases (166
prior plus nine), all 151 legacy ABI-6 byte comparisons, relevant harness tests
and all nine development gates. Preserve failed attempts and raw source/build/
execution pins. Apply Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 and
local CE/TD/TE review. No producer, shared ABI, standard, worker or sibling changes.
This private native experiment establishes no POSIX portability or production
architecture; fixed storage remains bounded by decision 0093, not a stack budget.

Preflight: all nine initial probes link at 2752–6504 bytes. Review then changes
the live fixture disposal to close/reclaim after observed stop 144 instead of the
normal-exit helper (which expects 18), and adds a final full retention check after
the last conflict/capture denial. No preflight image was executed. The fresh
complete native run consumes these reviewed source changes.

## Results and remaining scope

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

The fresh run records 529 commands and 421 frozen inputs, unchanged.
Maximum image: 7248 bytes under the unchanged 8192 bound.
All 162 of 166 prior ABI-15 images remain byte-identical.
All 42 harness tests pass. The retained preflight preceded the documented cleanup
and final-oracle review; the accepted witness contains the final source.

Prior-image review: 162 of 166 ABI-15 images are identical. The four capacity
images keep their sizes; their only changed bytes encode line numbers shifted
by the new 16-line method at unchanged unwrap sites, consistent with panic-location
metadata. Exact offsets and source correspondence are retained in
`prior-image-differences.json` in the evidence root. All four freshly pass.

## Final validation

All nine repository gates pass in `out/checks/run-hti9fxbz`, with unchanged checked inputs. The offline audit verifies 3,019 recorded native outcomes across 50 bundles; the new 175 cases also have fresh QEMU execution. Final logs and adoption records are retained under `docs/evidence/native-history-sealing-2026-09-06/`.
