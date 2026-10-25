# Actual bounded musl pthread lifecycle — 2026-09-06

The kernel conformance adapter runs actual source-rebuilt musl pthread_create,
start/exit and pthread_join in Aether. A native child uses musl's allocated stack
and initialized TLS, returns a value through join, unlinks from libc's thread list,
and exits through native clear-TID/wake before join unmaps its backing. Parent
and child retain distinct TLS/errno. Parent masks are restored and full allocation
quota is recovered. No kernel or sibling implementation changed.

This is restricted to default attributes and one joinable child per domain
lifetime. Attributes, cancellation, detach and further creation are explicitly
rejected. There is no signal-sending producer, async delivery, detached self-unmap,
timed join, general pthread compatibility or production userland adoption.
The [preimplementation contract](../../NATIVE-C.md#actual-bounded-pthread-lifecycle-contract--2026-09-06)
specifies the transport, ownership, bounds and verification.

## Verification

[Final results](final/results.json) retain exact commands and UTC boundaries;
final/sources.tar.gz freezes inputs. Hashes are checked before/after every command
and again before archival. All 142 selected target cases pass:

- Five lifecycle cases per memory profile: positive, supervised replacement,
  clone with rejected authority and checked cleanup, live-pin bypass rejected
  at assertion 216, and actual child #UD fault with peer completion.
- 132 earlier thread-family cases, including mask storage, fail-closed preflight,
  actual libc locks/waits/TLS and native stack/storage/wait/teardown boundaries.

Host checks pass 97 Python tests, Zig tests, standards/workflow and pinned C/Zig
formatting. The child delays completion so parent join reaches a native wait.
Join returns the expected pointer value, clears the native child and libc thread
list, and recovers quota without dereferencing the unmapped pthread handle.
Unsupported attributes and second creation preserve caller output; rejected
clone recovers its allocation and leaves no native child or list entry. Signal
sending, shared futex keys, timed waits and malformed futex flags reject explicitly.
The existing FD1 output and 64-parent-yield completion protocol are preserved.

Kernel hashes match native-signal-mask-2026-09-06, whose broader memory/image/M4
results are reused. Those suites were not rerun for this adapter-only change.

## Source and attempt retention

Original musl source/archive digest, COPYRIGHT, exact patch, private input
manifests and linked identities are retained. Source verification covers all ten
final lifecycle producers. Only pthread_create's recorded admission/preflight
patch and the disposable architecture syscall header differ from upstream.
Memory, VM, block, lock/wait, generic syscall-CP and join sources are unchanged.
Actual VM/lock routines are linked; no first-party no-op lock implementation is
used. The cancellation producer is explicitly rejected. Disassembly and ELF/tool
identities are retained. Upstream-only warning exceptions are in NATIVE-C.

Initial attempts 1–3 failed compilation on clone prototype, private GNU feature/
sign-compare and upstream C11 non-prototype declarations. Attempts 4–5 rejected
creation because the adapter omitted upstream clone's stack alignment step;
attempt 5 retained a temporary diagnostic narrowing that cause. Attempt 6 reached
successful lifecycle checks but failed the output write transport. Attempt 7
completed user checks and output but lacked the existing 64-yield completion
requirement. Attempt 8 passed all five cases. Final qualification followed exact
variadic typing, atomic diagnostic counting and stricter futex argument checks.
All attempts remain in target-attempts.tar.gz, inventoried by target-directories.json.
Failures are not counted as passing target cases. SHA256SUMS covers this packet.

## Remaining work

Independent review, actual companion acceptance, optimized/stress and hardware
coverage remain missing. Repeated thread creation, larger pools, resource budgets,
public synchronization APIs and consumer-required attribute/stack sizes need
qualification. The native filesystem and assembled serial shell/package release
remain unfinished. This proves the restricted libc lifecycle, not release readiness.
