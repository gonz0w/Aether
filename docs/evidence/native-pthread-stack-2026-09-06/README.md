# Bounded pthread stack attributes — 2026-09-06

The musl conformance adapter now accepts initialized joinable attributes with
page-aligned 128–256 KiB stacks and a 4096-byte guard. NULL keeps the default path.
Caller-owned stacks, other sizes/guards, scheduling, detach and nonzero reserved
fields reject before libc state or allocation changes. The internal C11 sentinel
also rejects explicitly. Production userland adoption is separate.

The 256 KiB fixture constructs attributes using actual musl APIs. It first reserves
backing until only 32 pages remain. Creation fails with EAGAIN, leaves no child or
output handle, and preserves that quota. Releasing the reservation allows a real
pthread to start, write/check 240 KiB of stack across yields, return through join
and recover the full quota. This retries a failed admission; it does not reuse a
successfully consumed child slot.

## Verification

The [contract](../../NATIVE-C.md#bounded-pthread-stack-attribute-contract--2026-09-06)
records requirements before implementation. [Final results](final/results.json)
retain exact commands and UTC boundaries, with frozen sources in
final/sources.tar.gz checked before/after every command and before archival.
All 150 selected target cases pass:

- Nine lifecycle cases per memory profile: default, supervised replacement,
  rejected clone authority, attribute-validation bypass (exact assertion 183),
  explicit 256 KiB stack, its supervised replacement, actual guard read fault
  (vector 14/error 4) with peer completion, pin bypass (216), and child #UD fault.
- 132 older thread-family cases, including masks, preflight, libc lock/wait/TLS,
  storage, stacks, timed/indefinite waits and original thread operations.

Host checks pass 97 Python tests, Zig tests, offline standards/workflow and pinned
C/Zig formatting. Unsupported attributes preserve caller output, errno, initial
mask, thread list/count/locking state and quota. Accepted stack geometry and live
pins are checked before the child is released. The guard test must fault rather
than time out; the peer must complete. The existing 64-parent-yield/output protocol
is preserved. A disabled attribute check cannot satisfy the rejection oracle.

The explicit positive stack size tested is 256 KiB; the NULL default exercises
musl's 128 KiB stack. Intermediate accepted sizes are covered by the range/alignment
predicate, not separately qualified target workloads. One successful child per
domain lifetime remains the enforced limit.

## Retention and remaining work

The initial eight-case suite passed; the attribute-bypass and per-rejection mask
checks were added before final qualification. There were no failed attempts.
All 23 target directories remain in target-attempts.tar.gz and are inventoried in
target-directories.json. before.tar.gz, implementation.diff, exact upstream patch,
original/adapted source manifests and disassembly are retained. Source verification
covers sixteen final lifecycle producers. SHA256SUMS covers the packet.

Kernel bytes match the prior signal-mask qualification. Unchanged memory/image/M4
results are reused by hash, not rerun. The libc archive and upstream source patch
are unchanged; this extends the original adapter and test harness. No sibling or
immutable pin changed. No companion acceptance, independent review, optimized or
stress/hardware coverage is inferred.

Next: safe repeated successful creation and larger thread-resource budgets, then
consumer-required synchronization and actual libzpool integration. This does not
qualify a filesystem or the assembled serial shell/package release.
