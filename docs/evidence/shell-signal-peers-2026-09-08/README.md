# Native action-record peer isolation

Before implementation: the private supervisor installs IGN/mask16 for signal10;
the client must still begin with DFL, install its own RX handler/mask4, and perform
normal I/O. Supervisor queries during complete requests, after client termination
and after reclaim must retain its own record across both generations. Use the
existing capability/lifetime and action-copy paths; no remote signal authority.

The negative build deliberately routes all action records to worker0's table.
It must fail the client's initial-DFL check (terminal89/owner1501), proving the
oracle rejects shared mutable state. Mark this fault option with negativeOption
and classify it as negative; release-artifact builds must refuse it. Preserve
existing profiles when unset. Select full command, M4 and host/pin regressions.
No delivery or new terminal tag; fixed private storage and user quotas unchanged.
This reuses the existing supervisor/client and avoids a new IPC protocol or owner.

The native option is release-rejected with the exact message retained in
release-rejection.log. It is a deliberate negative build, not a failed production
qualification. The default owner selector remains the active domain, and only
the record table is redirected in the fault control. All pointer checks still
use active-domain mappings, so a copied foreign pointer does not gain authority.

Rust uses pinned 1.98.0 edition2024 rustfmt and Zig uses 0.16.0 zig fmt. No new
dependency, assembly or wire protocol. Probe records are four stack-local u64
fields used synchronously by the existing raw trap; no pointer is retained.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build -Drelease-artifact=true -Dnative-signal-actions-shared=true
```

The last command must reject before producing a release artifact. The run uses
read-only Aether-userland/build/native-c-5olokhku and the retained native lock
zig-out/init-capacity-2026-09-06/tools.lock.json. Harness receipts record exact
commands and tool/source digests. collect.py archives native sources/artifacts and
verifies the prior packet and simplicity snapshot; manifest.json seals evidence.
No independent consumer acceptance, async delivery or full-dash claim.

The initial shared-table run failed owner1590 before the expected client terminal.
That first oracle incorrectly expected the client's initial-DFL check to detect
the mutation: admission zeroes the worker State, including its aliased table.
The retained first source/log has a common initialization/query error code.
The corrected peer query uses distinct owner1591, while installation remains
1590. The final oracle requires owner1591/reclaimed0. It does not infer a client
terminal or recovered cleanup. Earlier successful host/M4 logs and failed native
artifacts are preserved; final checks rerun on frozen corrected sources.

Final results: all 250 command-runner cases and seven M4 target cases pass.
Host/pin checks pass, including 98 Python tests. The positive peer completes two
generations and four reclaims; the shared-table negative rejects exactly at
owner1591/reclaimed0. Supervisor raw code is 4,920 bytes, below its 8,192-byte
limit. Runtime sources stayed frozen throughout the corrected qualification.
The initial native oracle failure and initial successful host/M4 attempts are
retained alongside the final evidence; no failed attempt was discarded.

This closes native action-record peer isolation only. Next is bounded pending
self-delivery under a private signal-capable owner, followed by retained signal
termination and reuse. Public signal routing, guarded live-handler/nonlocal
injection and consumer acceptance remain open.
