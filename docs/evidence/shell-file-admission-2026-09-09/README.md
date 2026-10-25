# V4 file-root admission boundaries

All384 command cases and98 Python host tests pass, including offline pin/workflow
checks. No unexpected failed target attempt.

This packet records the existing command harness's qualification of V4 admission
rejection. See qualification.json for final case counts and frozen artifacts.
It does not qualify the remaining file-description or interrupted-I/O matrix.

The fifteen new selections extend the existing root profile:

- Missing root; aliases to input, output, diagnostic and CWD; invalid rights,
  kind, generation and reserved tail byte.
- EOF after192,208 and223 total bootstrap bytes: absent, partial and one-byte-short
  final root record. Completion is bounded and the owner closes its writer.
- V3 sender/V4 receiver and V4 sender/V3 receiver. These send only the header and
  close, so they establish header rejection and teardown, not queued-body recovery.
- A broken early publication before reserved-byte validation must fail the
  unpublished-state oracle: client113/owner1501, with zero reclaims.

Each of the fourteen normal rejection cases requires client110 and unpublished
descriptors, identity and CWD. V4 receivers additionally require an unpublished
file root and public open returning EAGAIN before and after failed admission;
the V3 receiver retains its existing profile and has no file-root facade. No client protocol request may reach the owner, and
file open/read counters remain zero. Empty stream sinks and observed terminal
order client110/stream17/file17 are required across both generations, with exactly
six reclaims. Backend file connections use fresh service instances; no old
composition probe consumes an open slot. The earlier actual dash execution and
all previous command cases remain in the complete suite.

The early-publication mutant is a semantic failure control; it is not a successful
resource-recovery result. Its owner rejects before reclaim. VM teardown remains
a separate harness obligation. Normal malformed admission does have successful
native teardown evidence.

Scope: C client admission observations, test-only early publication, Rust fixture
inputs/expectations and the existing harness lifecycle oracle. No production
parser weakening, new native API, resource expansion, sibling, upstream object,
service protocol, SDK default or released pin change. Compact C style is retained
under DEVELOPMENT's migration exception; Rust formatting uses edition2024.
No fresh M4 run is selected because kernel/shared transport/build behavior is
unchanged. Independent consumer intake, file exhaustion/stale/offset controls,
ambiguous backend recovery, ENV execution and the assembled release remain open.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 scripts/check_workflow.py
python3 docs/evidence/shell-file-admission-2026-09-09/collect.py
```

The collector verifies frozen runtime sources, the prior sealed root packet and
the simplicity snapshot, and reads back source/artifact archives. The recursive
manifest seals these results. Source changes during qualification are forbidden.
