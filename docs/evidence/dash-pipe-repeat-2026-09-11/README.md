# Repeated actual dash command substitution

Status: qualified for the scoped native producer cases below. See [PLAN](PLAN.md).

One pinned actual dash parent executes two `$(echo pipe)` substitutions and prints
both results. Each child closes its pipe aliases, exits0 and is collected through
real musl wait3. The owner verifies `pipe\n` through EOF for each generation,
retires each pipe and reclaims each child after wait ACK. The surviving parent
retains identity and stdio holders while child/pipe/freeze generations advance.
Independent backend readback must equal `pipe\npipe\n`; a fresh second shell runs
builtin `echo clean` and verifies `clean\n` in a fresh backend lifetime. Two parents,
two backends and two copied children give six actual reclaims without kernel or
quota changes. No dummy worker or fabricated output is used.

Stale freeze token1 on copy2 rejects at2179 after one reclaim. A pipe-generation1
reference in the second receipt makes the real child exit80 before readiness;
owner2180 rejects after one reclaim. Unknown copy-stage exit80 bypasses descriptor
cleanup traffic only in this opt-in client. Existing single-substitution and
fault/stop/SIGPIPE consumers remain unchanged.

Run existing pinned commands:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Scope: private producer, fixed two-cycle workload, bounded stream backend.
Serial substitution, live-pipe exec, general recovery/interruption, installed SDK,
independent userland acceptance and R1 assembly remain open. No sibling, kernel
source, resource quota, released standard or upstream object changed. The simplicity
tradeoff and preimplementation invariants are in PLAN. This extends the existing
owner, with no new service, allocator, dependency, unsafe block or wire format.

Implementation self-review: caller authority comes from the connected route.
Parent identity, child identity and pipe references are checked independently.
Reclaim happens only after terminal plus wait ACK; retirement requires closed
holders and empty pipe request slots. The current ACK frame carries no pipe I/O,
and its response completes before retirement. Old frame storage is cleared before
the next iteration, and the reclaimed child route is skipped within that iteration.
The no-child shell accepts no pipe creation and must leave stderr/input positions
unchanged. Independent reader review and broader failure recovery remain open.


The first full suite passed127 cases, then rejected the receipt control's correct
runtime trace because the harness expected child generation2 before generation1.
The intended trace is child1 exit0, child2 exit80, then owner2180/reclaimed1.
Only the ordered-context assertion was corrected; no runtime source changed.
The failed suite and its matching preflight source snapshot are preserved.
Work resumed on2026-09-13; this packet retains its original plan/start date.

## Results

All 271 connections, five launch and two console cases pass (278 QEMU cases).
Focused positive and both stale-generation controls passed on their first attempt.
Host/harness, scoped Rust/C format, workflow, three released pins, simplicity and
explicit incompatible-configuration rejection checks pass. Every previously
qualified copied public-fork client ELF remains byte-identical. Final qualification
sources stayed frozen. The first full run failed an incorrectly ordered receipt
assertion; its correct runtime trace, sources and artifacts remain archived.

The maximum owner image is 11888 bytes under the unchanged16KiB bound. This does
not measure worst-case stack, peak memory or performance. Exact commands, tool
identities, hashes, raw traces, source snapshot/patch and target artifacts are
retained. Archives were read back and hash verified before removing the unpacked
preflight duplicate; final suite outputs remain available. Independent reader and
installed consumer acceptance remain separate.
