# Experimental musl disposition routing

Qualified 2026-09-08: 286 command-runner cases, seven M4 target regressions and
98 Python tests plus host/pin/workflow checks pass. No failed or interrupted
qualification attempts. Sources were frozen during all qualified runs.

The new cat-roles-startup-public case uses the pinned SDK's actual musl sigaction,
signal, restorer and sigsetjmp/siglongjmp. It proves public/private native record
agreement, DFL/IGN/custom registration, unused public argument registers and
private reserved-register rejection, unsupported SA_RESTART, bad-pointer/output
and NX-handler rejection without record mutation, normal handler return and
nonlocal mask restoration. Exact copy and two generations/four reclaims finish.
The disabled-routing control rejects client101/owner1501; previous startup modes
explicitly check public raw ENOSYS. No alternate C disposition table is compiled
in the public selection. Other fixtures preserve their existing table.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
python3 docs/evidence/shell-signal-public-2026-09-08/collect.py
```

Host, native and M4 logs and matching results are retained here. The collector
verifies the previous close packet, frozen source receipts and the simplicity
snapshot, then reads back every source/target archive member against its digest.
qualification.json identifies the exact run directories and counts; manifest.json
seals this packet. The previous read-only source review remains separate.

Runtime changes: one opt-in build selection, public dispatch to the existing
checked action operation, and correct public four-argument validation. Existing
per-domain ownership, RX checks, copy transaction, record quota and cleanup remain.
No public signal production, restart semantics, legacy terminal-tag change,
sibling edit or pin update. Actual dash/consumer acceptance, broader delivery,
child notification and process/I/O composition remain unqualified.

Review follows the pre-code routing and simplicity assessment in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#public-signal-routing-review--2026-09-08).
No independent reader/owner sign-off is implied by these tests.
