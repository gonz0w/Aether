# Channel acquisition evidence — 2026-09-06

Decision 0050 / BG-058. Seven new tests cover reserved capacity, channel creation
success through cleanup, four selected create errors through local empty cleanup,
pending/invalid reservations, malformed reply retention, failure after resource
acquisition and independent channel/native/service generations. The reservation
omission control fails by assertion as required.

Commands from the sys-init repository:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-channel-acquisition-20260906.json > /private/tmp/sys-init-channel-acquisition-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

model.json/model.log retain 228 passing tests and 23 distinct mutation controls,
100 seeded traces and a 1,000-trace benchmark. validation/ retains run-3f8osy7q:
all eight offline gates pass, including 228 model, 48 host and 37 harness tests.
sources_unchanged is true. No failed attempts occurred. Final decision/planning
validation notes were appended afterward; executable model inputs remain unchanged.
All model input hashes match their source/ copies.

reviewed/ retains the inspected native_channel.zig from the sibling checkout and
the previously frozen native_c.zig from decision 0042. reviewed-files.json records
both source locations and hashes. This is an explicit source review, not a claim
that this pair is a fresh built producer. The sibling is not a runtime/test input.

The model reserves attempt/native slot capacity before the synthetic factory call.
Create success retains both endpoint IDs before binding; selected create failure
records an uninvoked logical launch and qualifies empty cleanup without a native
launch/reclaim receipt. Unknown/malformed creation closes the owner and retains
its reservation. No actual channel or process was created by these tests.

BG-058 next specifies and executes fresh consuming native acquisition/rejection/
cleanup witnesses on pinned artifacts. Larger graphs, stop/force automation and
unknown recovery remain open. No native source, shared release or pin changed;
no fresh native execution was performed. SHA256SUMS.json covers every bundle file
except itself.
