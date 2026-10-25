# Inherited-stream pre-copy rollback — 2026-09-10

The inherited-stream owner now recovers from the existing injected native copy
ENOMEM while its parent remains frozen. It verifies the destination is unpublished,
checks ownership of the four staged endpoint ends, closes them and verifies access
is denied. Only staged child holders are removed. A stale cancellation token must
leave the source frozen; matching cancellation releases it with EAGAIN. The parent
then consumes the existing failure-completion protocol, keeps FD 10/CLOEXEC, reads
a/b from its original position and performs final backend closure.

After parent73/backend17 cleanup, the existing backend image is admitted into slot2
at the original expected generation. Its hello, three stream closes and terminal17
prove the failed copy did not consume that lifetime. Exact terminal order0=73,
1=17,2=17 repeats twice, with six reclaims. Replacement admission follows original
channel cleanup to respect the existing three-generation channel limit.

All 36 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. The three rollback mutants require precise failures:

- rollback-leak retains one staged endpoint: owner1972, zero reclaims.
- rollback-close closes the still-held backend input: owner1952, zero reclaims.
- rollback-cancel leaves the source frozen: owner1973, zero reclaims.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#inherited-stream-pre-copy-rollback-selection--2026-09-10)
records requirement, ownership, test selection, lifetime bounds and simplicity
tradeoffs. Parent recovery and backend cleanup are shared with the preceding
publication-recovery path; no second transaction service, new pool or public
fork/errno contract is added. The new C fixture accepts exactly the cancellation
EAGAIN; the existing freeze assembly and kernel remain unchanged.

## Retained failed attempt

connections-suite-63dkw_rm passed the existing32 cases, then the first rollback
case completed parent73/backend17 and rejected replacement189/owner1950 with two
reclaims. The reused backend requires argv[0]=worker; the generic slot2 helper
supplied client. This is a fixture integration failure, not a successful rollback
qualification. Exact sources, report, logs, timing and artifacts are retained in
attempt-1 files and the target archive. The correction supplies worker only for
inherit_rollback slot2, preserving backend validation and the original oracle.
The three new negative cases had not run in that failed attempt.

The final run completes all36 cases. Kernel/build hashes and 22 older raw connection
envelopes match the preceding packet, excluding only the48 fresh entropy bytes.
The inheritance cases retain their prior oracles and pass on the refactored owner.
Two representative command-owner images (base and file-service composition) rebuild
byte-identically against their retained artifact hashes. This is static comparison,
not fresh command runtime acceptance. The previous431-command/M4 execution evidence
remains historical: the new startup label is enabled only in the rollback cfg,
while kernel and shared command adapters are unchanged. Full connections, launch
and host checks are the selected fresh runtime coverage. Maximum owner size is
5,848 bytes, within8,192. No sibling sources or released standards pins changed.

General admission failures, incomplete publication messages, shared backend
uncertainty, arbitrary descriptor tables and signal-aware preparation remain open.
Current clients are single-context with custom signal delivery disabled. Native
fork/exec/wait SDK adoption, full dash, independent consumer acceptance and R1 remain
unfinished; neither injection coverage nor passing inventory checks settles them.

Sources stayed frozen during each target attempt. Timings retain exact commands,
UTC start/end and exit status. Reports bind SDK/tool identities and source hashes;
archives preserve final and failed target artifacts and extracted musl headers with
COPYRIGHT. Compatibility, formatting and the pinned simplicity snapshot have
separate receipts. The collector checks the previous packet, final source hashes,
failed source snapshot and archive readback; manifest.json seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 final source files and
1393 target artifacts, including the failed attempt. All final
selected suites stayed within their documented review budgets.
