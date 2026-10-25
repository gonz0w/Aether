# Native taskq runtime integration — 2026-09-07

The [preimplementation contract](contract.md) binds the scoped work to
[NATIVE-TASKQ](../../NATIVE-TASKQ.md). Both final profiles pass: 46 lifecycle cases each, 92 total, including eight
taskq cases per profile. This is bounded native conformance-fixture acceptance,
not production libc/filesystem support or release readiness.

## Attempts retained

- Initial build/boot 1 linked but was rejected as invalid native ELF: removing
  the unrelated lifecycle cookie also removed the required PT_TLS segment.
- Build/boot 2 restored a meaningful per-worker TLS cookie and passed both native
  domains. It is preliminary positive evidence, not final full-suite coverage.
- Default suite 1 passed taskq and its positive supervisor replacement, then
  rejected the allocation-failure image as invalid supervised ELF. Optimizing its
  early fatal branch removed all later TLS accesses. No negative oracle passed.
- Default suite 2 moves a volatile TLS check before all fatal branches. It also
  tests actual pthread_create third-child rejection without allocation and fills/
  rejects/returns the arena's four spare slots before queue entry allocation.

No loader/kernel bypass or capacity change was made. The required native TLS
shape is now exercised by the fixture itself, including failure variants. Original
and adapted OpenZFS sources and musl source/header receipts remain in build outputs.

## Accepted results and limits

Final default suite 2 and large suite 1 bind identical, unchanged source hashes.
All 32 kernel/build inputs match the preceding detached-thread qualification.
The taskq/platform objects are byte-identical to the earlier layout-qualified
objects: queue 384 bytes, entry 40 bytes, eight 512-byte slots in one page. Both
profiles' six native variants retain the exact original source prefix and helper
append. There are no unresolved external symbols. LLVM's symbol table retains
the same local hidden zero-valued `_DYNAMIC` sentinel as the detached baseline;
the first overbroad audit assertion and refined symbol inspection are recorded.

Positive checks execute real musl-backed upstream taskqs, A-to-B dependency,
parent whole-queue draining including a queued tail, taskq TSD ownership and TLS
isolation, duplicate constant IDs, delayed/cancel rejection, entry reuse, actual
third-pthread rejection, arena exhaustion/return, two generations/four admissions,
early-unmap denial, exact stop/unmap/retire and quota/list restoration. The five
negative variants fail at 328/329/303/302/312 as specified, never at a watchdog.
Both positive and allocation-failure supervisor replacement pass. The latter
reclaims three domains and admits a fresh generation that reaches the same
intentional allocation failure; it does not claim application-state recovery.

All 98 Python tests and Zig host/pin/workflow checks pass. Clang formatting and
diff checks pass. Sources, producer receipts, original/adapted inputs, symbols,
serial logs and attempt results are retained in the artifact archives. ISO files
and duplicate installed boot files are omitted from those archives; accepted ISO
hashes, build commands and native executable envelopes remain in the receipts.

Reproduce using the exact SDK/tools paths and command in NATIVE-TASKQ, once per
profile. Each suite creates a fresh owned output directory and preserves failures.
The source/header and tool pins remain unchanged; sibling repositories are read
only. Original OpenZFS definitions retain their CDDL notices and full license/
copyright in the source snapshots; original adapter code remains BSD-2-Clause.

Next: measure live full-engine thread/stack/allocator demands before selecting
production budgets. Two native taskq workers do not establish a two-thread ZFS
engine, scalable service policy, persistent filesystem acceptance or independent
consumer sign-off. Linux attribution figures are cumulative, not live peaks.
