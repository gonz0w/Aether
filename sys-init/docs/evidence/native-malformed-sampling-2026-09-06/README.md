# Bound malformed sampling evidence — 2026-09-06

Decision 0082 passes 136 native cases: all 127 prior oracles plus six labelled
malformed-reply probes and three omission controls. Each probe omits exactly one
selected S/O2 syscall and injects a synthetic raw triple; other received samples
are real. Exact data and local causes survive while Driver closes admission and
retains worker, reader, token, pending index and generation, with no terminal fact
or invented native errno. Further sampling denies without another read.

Six positives finish 100/reclaimed=3 after asserted retention and known fixture
cleanup. Skip closure, forget reader and invent errno controls reach 1043/0,
1044/0 and 1045/0. All 183 frozen inputs unchanged; 90 of 127 previous images
are identical. Largest image remains 4048 bytes; new images fit 3760–3872 bytes.
The first run's one-reclaim completion was rejected by the kernel and is retained;
the corrected run preserves the required three-reclaim positive oracle.

This is synthetic NT-04 qualification executed in the native fixture, not malformed
kernel output or a lost reply. Admission is still fixture-seeded. Next: NT-05
explicit synthetic interruption after O1/S, retaining resources and partial history
without retry/application; NT-06/07 pending-history bounds, full launch composition,
BG-057 consumer retirement and BG-033 recovery remain open.

See witness/README.md, exact invocation.json, source/artifact comparison and the
separate failed-run-1. Both preflight versions preserve sources, maps and logs.
The kernel positive oracle is unchanged; failed evidence is not reclassified.

Validation: all nine development gates pass in `out/checks/run-3o3jd65e`.
The offline audit now covers 1915 historical native outcomes across 43 bundles;
this is separate from the fresh 136-case target witness. Ten current consumer
inputs and unchanged worker/builder sources match their executed/build snapshots.
The 38 harness tests and nine named host validator tests with two omission
controls pass. Validation artifacts, current adoption records and the failed
first native attempt are retained with the evidence.
