# Native terminal evidence contract — 2026-09-06

Decision 0075, BG-058 ND-02. This is source review and a local contract/test plan,
not a worker-status implementation, new native witness or independent sign-off.
Seven reviewed files are copied under source/ and pinned by reviewed-files.json.
The kernel source was selected from decision 0074's frozen-inputs and verified
against its sources.json, not taken from a mutable companion checkout.

native-source-comparison.json pins all seven current sys-init native consumer
inputs, verified unchanged against decision 0074's executed 89-case witness.
validation/ preserves two passing full-check runs: initial run-y5rb1zpa and final
run-w4axn51_ after clarifying global sample capacity and positive terminal revision.
The final reports cover eight gates, 228 model tests, 23 negative controls,
1000 traces, 48 host tests and 37 harness tests. Historical native catalog verification
is not new native execution. Exact command: python3 scripts/check-all.py.

adoption/ retains the final decision, contract, scope records and work order.
Only validation notes and evidence copies followed the final checks. Local links
and git diff --check pass. No release bytes, consumer pins or historical evidence
changed. SHA256SUMS.json inventories this bundle excluding itself; hashes establish
byte identity, not authority or runtime conformance. Next: NT-01–02 native probes.
