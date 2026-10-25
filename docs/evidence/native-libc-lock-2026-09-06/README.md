# Actual contended musl internal locks — 2026-09-06

The bounded libc/TLS fixture now runs unchanged, source-rebuilt musl 1.2.6 __lock
and __unlock through the existing native private-futex adapter. The parent acquires
a lock and writes protected data. The child must register as blocked inside musl's
contended acquisition before the parent unlocks. The child then acquires, verifies
and updates the data, and unlocks. After native join, the lock word must be zero
and the protected update visible. No kernel ABI or implementation changed.

The [preimplementation contract](../../NATIVE-C.md#actual-musl-internal-lock-contract--2026-09-06)
defines ownership, resource limits and selected verification. This exercises signed
lock-word/congestion values through the adapter, not just an uncontended fast path.
The fixture enables libc.need_locks but does not publish a libc thread-list entry
or implement pthread creation, public pthread mutex APIs, signals or cancellation.

## Verification

[Final results](final/results.json) retain exact commands, UTC boundaries and
[frozen sources](final/sources.tar.gz). All selected checks pass:

- Nine lock cases per memory profile: positive, supervised replacement,
  descriptor/output aliasing, blocked-child stop/replacement, guard fault with
  peer completion, pin bypass at assertion 194, wrong self-pointer at 291,
  dropped wake at 289 and disabled locking at 286.
- Sixteen libc wait, twelve no-deadline, fourteen libc TLS, twelve storage,
  twelve stack, twelve timed-wait and fourteen older thread cases: 110 target
  cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks, and
  pinned C/Zig formatting.

Success requires observed native blocked registration, actual adapter wait/wake
calls, protected data changing from one to two, and a zero lock word after release.
The disabled-lock control must fail because the child never blocks; a watchdog
timeout cannot substitute for exact assertion 286. Existing TLS, errno, FP, authority,
pointer, aliasing, guard and stop/replacement checks remain. The count-one wake
translation still depends on the current two-context domain limit.

## Source identity and retention

__lock.c and __wait.c come from the verified musl archive. Their source bytes are
unchanged; the only private-header replacement is the existing first-party syscall
transport in the disposable build. Objects link before the supplied libc archive.
[Source verification](source-verification.json) checks all fourteen final producers,
including original/adapted manifests, upstream source hashes and notices. The
original source and COPYRIGHT are in `consumer-source-review.tar.gz`, identified
by `review-inputs.json` and `libc-receipt.json`. `lock-disassembly.txt` and
`disassembly.json` retain the actual linked lock/unlock code and tool/object/ELF
identity. Upstream formatting is preserved; original C retains strict warnings
and pinned formatting.

The initial nine-case suite and full final qualification pass; there were no
failed attempts in this change. All seventeen target directories are retained in
`target-attempts.tar.gz` and inventoried in `target-directories.json`.
`before.tar.gz`, `contract.md`, initial logs and final source snapshots remain.
No sources changed during final qualification; hashes were checked again before
archival. SHA256SUMS covers this packet. No sibling source or immutable pin changed.

## Remaining work

This qualifies the selected internal-libc lock transaction and domain-replacement
cases, not general mutex support, arbitrary owner death, recursive/robust locks,
larger thread pools or stress performance. Actual libc creation/start/exit and
join adaptation still require signal and lifecycle work. Main TLS extents, repeated
creation and engine resource budgets remain open. Kernel bytes match preceding
qualification; memory/image/M4 suites were not rerun for this fixture-only change.
No companion acceptance is inferred. Independent review, optimized modes, stack
high-water and extended stress remain missing. Top-level timestamps do not cover
every internal libc-builder command. The native filesystem and assembled
shell/package release remain unfinished.
