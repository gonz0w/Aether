# Bounded repeated pthread lifecycle — 2026-09-06

Native retirement opcode 0x2800a requires the current domain thread capability,
parent execution, the exact child ID, and a stopped child with no exit address or
pending wait. It clears the child record without unmapping memory or restoring
admission budget. Four successful admissions are allowed per domain lifetime,
with distinct IDs and one live child at a time. Failed creation consumes none.

The first-party conformance wrapper calls unchanged musl __pthread_join, then
retires using the saved native ID. It never reads the unmapped pthread handle;
retirement failure closes that handle and keeps admission closed. This does not
provide general stale pthread_t detection or production userland adoption.

## Verification

The preimplementation contract is in docs/NATIVE-C.md and contract.md. Final
results retain exact commands, source hashes and UTC boundaries. Sources are
frozen in final/sources.tar.gz and checked before/after every command and archival.
All 197 selected target cases pass: 24 lifecycle, 132 older thread-family,
25 memory, 9 image and 7 M4 cases. Host checks pass 97 Python tests, Zig tests,
standards/workflow and pinned formatting.

Each repeated fixture completes four actual 256 KiB pthread create/exit/join
cycles. Each cycle exercises allocation-pressure failure/retry, 240 KiB of stack,
fresh TLS, isolated errno/masks, returned value and full allocation-quota recovery.
It rejects live-child retirement, old IDs, duplicate retirement, child-side
retirement and a fifth admission. The same-ID mutant must fail at assertion 233.
Both memory profiles include direct and supervised replacement runs; the older
attribute, guard-fault, authority, pin and child-fault rejection cases still pass.

## Retention and limits

The initial compile failed because macro-renaming __pthread_join conflicts with
musl's stringized weak alias. The correction uses a strong public wrapper calling
the unchanged internal symbol. The failed attempt, corrected initial 12-case pass
and final runs are retained: 28 target directories, 26 from final qualification.
Source verification covers eighteen final lifecycle producers against the pinned
musl archive. Only the existing syscall adapter and pthread-create admission patch
change upstream bytes. Original/adapted manifests, exact patch, disassembly,
before snapshot and implementation diff are retained. SHA256SUMS covers this packet.

No sibling or immutable pin changed. Independent review, companion acceptance,
optimized/stress/hardware coverage and complete POSIX support remain outstanding.
Next: consumer-required concurrent thread resources and synchronization before
actual libzpool integration. A persistent filesystem and assembled serial
shell/package release are still unfinished.
