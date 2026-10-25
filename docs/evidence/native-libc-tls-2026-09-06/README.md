# Actual musl TLS in a native child — 2026-09-06

The existing child storage ABI now has a consumer witness using musl 1.2.6's
actual __copy_tls implementation. A bounded fixture initializes the selected
private pthread fields, then the child calls pthread_self, the errno accessor
and snprintf with its own copied TLS and stack canary. Child TLS/errno mutations
remain separate from the parent across scheduling and native exit/wait completion.
No kernel operation or companion implementation changed.

The [preimplementation contract](../../NATIVE-C.md#native-libc-child-tls-integration-contract--2026-09-06)
defines ownership, selected operations, resource bounds, denied claims and tests.
This is not pthread_create/join: there is no libc thread-list publication,
signal/cancellation implementation, general locking or TSD support. Child creation
and exit still use the existing native grant. Only the selected libc calls are
qualified; this adapter is not a replacement production libc threading layer.

## Results and identity

[Final results](final/results.json) bind exact commands, UTC boundaries and
[frozen sources](final/sources.tar.gz). All selected checks pass:

- Seven libc TLS cases in each memory profile: positive, supervised replacement,
  descriptor/output aliasing, stop with a blocked child, guard fault with peer
  completion, skipped pin rejection at assertion 194, and wrong self-pointer
  rejection at assertion 291.
- Twelve storage, twelve stack, twelve wait and fourteen older thread cases:
  64 target cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks, and
  pinned C/Zig formatting. A mismatched private-header source pin is additionally
  rejected before compilation in `header-pin.log` and `pin-rejection/result.json`.

The child cookie must start from the actual TLS template, then retain its own
value through yields. The parent's cookie and errno retain their separate values.
The new helper is stack-protected C; `libc-disassembly.txt` records calls into
__copy_tls, __errno_location and snprintf, plus canary load/check and failure path.
The public pthread_self symbol shares implementation with thrd_current in this
musl build. Tool/ELF identity is in `disassembly.json`.

The builder verifies the supplied libc archive against its receipt, then verifies
the musl source archive against that receipt before extracting private headers.
`libc-receipt.json` and `musl-source.json` retain those identities. Each producer
retains the extracted private headers, COPYRIGHT and per-file hashes. Headers come
from the pristine pinned archive, not a mutable sibling checkout. Upstream private
headers are system includes; first-party code retains -Wall -Wextra -Werror.
The hidden visibility macro matches upstream src/include/features.h. TLS copying
must fit the middle 4096-byte page of the declared three-page allocation; larger
libc TLS requirements reject rather than truncate. This is a fixture limit, not
a measured engine-wide TLS or stack budget.

## Attempts and remaining work

The first compilation failed on the missing musl internal visibility definition
and upstream-header diagnostics. The next failed on a signed comparison in the
first-party helper. Both were fixed; no target ran in those attempts. The initial
six-case suite then passed. The wrong-self-pointer control was added before final
qualification, which passes seven cases per memory profile. Every attempt is
retained, including both failures, in `target-attempts.tar.gz`; the thirteen
directories are inventoried in `target-directories.json`. Initial sources and logs,
the preimplementation contract and source-pin rejection are retained alongside
final results. No inputs changed during the final run. SHA256SUMS covers this packet.

Kernel bytes did not change; memory/image/M4 target suites were not rerun for this
fixture-only change. Their preceding qualification remains historical scoped
evidence. No sibling source, consumer pin or acceptance changed. Actual pthread
creation/join, main-context TLS extent registration, signal/cancellation and
repeated-creation semantics, engine resource budgets and the native filesystem
service remain unfinished. Independent review, optimized kernel modes, stack
high-water and extended stress are open. Top-level timestamps do not cover every
internal libc-builder command. This is not assembled shell/package release readiness.
