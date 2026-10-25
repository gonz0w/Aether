# Bounded session runtime extraction — UL-007

The separate [ABI29 filesystem-profile candidate](../../docs/proposals/SESSION-FS-ABI29.md)
now adapts startup identity, parent-only branches and wait PID validation for
shell1/children2–4 in the seven-domain composition. Host/object checks pass;
the [complete link and initial backing checks](../../docs/evidence/session-abi29-link-2026-10-21/README.md)
now also pass. Matching dispatcher, runtime fit and native filesystem shell remain open.
Existing ABI23/24 builders and sealed deliveries remain separate.
Select the [v2 boot-parent input](../../docs/evidence/session-abi29-boot-parent-2026-10-21/README.md):
the actual generation0 supervisor is PID7. Earlier candidates'14/21/28-only
parent validation is incompatible with this boot profile; their bytes remain sealed.

Aether-userland owns this implementation by explicit maintainer assignment on
2026-09-29. Aether retains native ABI/grants/enforcement and the fixture owner.
This experiment extracts the private AENMX008/ABI23 session client into runtime.c
and application.c. It does not publish an SDK or implement general POSIX services.

runtime.c owns existing bootstrap/channel/process/FD/mask state and finalization.
application.c supplies dash arguments/environment and narrows helper paths.
session.h exposes one startup operation and application admission callback; a
copied child inherits startup state, and a replaced image starts fresh. Repeated
startup is rejected before further channel transfers. The callback does not grant
native rights: the unchanged native owner enforces actual image admissions.

Borrowed source and notices remain verbatim under vendor/; provenance.json binds
them to the independently accepted serial source export. Existing musl CRT/libc
and upstream public fork/wait code retain their own terms and native patches.
components.py rejects missing, duplicate, stale and wrong-profile receipts before
linking, including memory adaptation that stock musl could otherwise supply.
This developer gate does not enforce capabilities against a bypassing caller.

[Change review](../../docs/evidence/session-runtime-extraction-2026-09-29/review.md)
records pins, scope, tests and limits. The source extraction now passes49 fresh native executions
and49 independent comparisons across serial and preserved007 workload families;
null/repeated startup is exercised natively. The sealed standalone008 candidate
rebuilds identical extracted parent/helper ELF bytes. See
[results](../../docs/evidence/session-runtime-extraction-2026-09-29/README.md).
All SSDK-01–06 promotion dispositions and independent review remain open;
old serial acceptance remains the reference for the original artifacts.
No current accepted path is replaced or historical evidence rewritten.

## Builder dependency selection correction

[Cached-module evidence](../../docs/evidence/session-runtime-build-imports-2026-09-29/README.md)
reproduces an ordinary-import cache bypass of missing-component validation. The
corrected rebuild.py loads the two verified support files into local module
objects, without changing caller import paths/cache. Fresh builds retain the same
native-qualified ELF bytes. Use the corrected candidate seal for new rebuilds;
prior archives remain immutable and independent review remains pending.

## Minimum Python compatibility

The builder and component validator support Python3.10+.
[Actual3.10.21/3.14.7 qualification](../../docs/evidence/session-runtime-python310-2026-10-03/README.md)
replaces newer-only hashlib.file_digest calls with streamed SHA256, preserves
component/support selection, and rebuilds identical native-qualified ELFs. Select
the new candidate seal for new builds. Earlier evidence/bundles remain immutable;
independent reader review and SDK promotion remain pending.

## Explicit ABI24 endpoint waiting

SESSION_CHANNEL_WAIT requires SESSION_SERIAL and a matching AENMX009/ABI24
kernel/owner composition. It selects channel-transfer.h through wait-transport.h.
The latter is derived from the frozen vendor transport whose SHA256 is
`d4796885dc2a9c16a9fd6b848ebed0b2420063e1f126196e2404dc361c22cbbd`;
only vendor include paths and the transfer selection differ. Frozen vendor bytes
and provenance.json remain unchanged. The default path still includes that exact
original transport and preserves ABI23 whole ELF bytes.

After EAGAIN, wait0x24004 receives the same endpoint and all-zero reserved args.
A zero readiness hint retries the transfer at the unchanged partial offset. EOF,
invalid/oversized transfers and nonzero wait results poison the protocol. This
includes EINTR: the adapter does not dequeue/deliver signals, inject handlers,
claim SA_RESTART or replay ambiguous transactions. Ordinary FD transactions
retain their existing outer native signal mask. Unsupported wait does not fall
back to polling. Broader interactive signal semantics remain open.

The sealed builder admits009 only when both runtime compilation steps explicitly
select waiting; component admission must receive the same expected profile.
[Consumer evidence](../../docs/evidence/session-channel-wait-consumer-2026-10-03/README.md)
records host fragmentation/error controls, exact legacy rebuilds and native delayed
input. This private profile does not promote the SDK or widen fixture lifetimes.
