# Session SDK integration boundary — UL-081 / UL-007

2026-09-29. UL-081's current boundary assessment is complete. The maintainer assigned bounded libc/POSIX runtime implementation to
Aether-userland on2026-09-29. Implementation is complete for the bounded candidate; independent review remains pending. This is a local consumer
handoff, not a shared standard, published SDK API or authorization to edit siblings.

The supported experimental link boundary is the exact component closure accepted
by SERIAL-SESSION-01–06, explicitly selected by private AENMX008/ABI23. The unchanged
musl archive alone is insufficient. Bootstrap/startup facade, memory adapter, public
fork/wait/rebind objects, native dash main/jobs/input objects, CRT and libc all have
independent pins. A new application or profile requires new authority/acceptance;
copying the current fixed shell wrapper into an archive cannot establish that.

[Static audit](evidence/session-sdk-boundary-2026-09-29/README.md) reproduces the whole
accepted parent ELF exactly. Removing its facade fails on __wrap_main; removing its
process objects fails on copy_rebind; duplicate facade fails on strong definitions.
Removing memory adaptation still links, but __mmap/mmap, mprotect and munmap resolve
from musl archive members instead of libc-adapter.o. That different ELF has no native
qualification. A link command and zero linker exit are not component-admission proof.

## Selected responsibility and state boundary

Retain musl's CRT, allocator, public sigaction and internal signal helpers. Public
sigprocmask and internal __block_all_sigs/__restore_sigs must observe the same native
caller mask. The earlier duplicate local mask was already eliminated. Memory
protection must retain the strict musl patch; ENOSYS cannot count as protection.
Interpose only the explicit bounded native operations, keeping unsupported calls
and profile restrictions visible. Do not overwrite libc or return successful no-ops.

The future runtime extension must separate application main/helper semantics from
one per-process bootstrap and process/descriptor/signal state. Owner channels and
native grants establish authority; paths, package metadata, UID1000 and FD numbers
do not. Copy inheritance, TLS/libc rebind, exec replacement/CLOEXEC, shared FD
positions, EOF, poisoned transport, terminal collection and reclaim stay tied to
exact parent/child generations. No new global POSIX server or generic VFS is chosen.
008's UART remains owner-only;007 must continue rejecting direct UART access.

Aether owns native ABI, grants and the existing fixture owner. Aether-userland now owns the bounded libc/POSIX runtime
implementation, SDK experiments and consumer replay by explicit maintainer agreement;
pkg-mgr owns eventual recipe/transport policy and sys-init owns service policy.
This assignment covers the bounded runtime extension only; general POSIX services
and sibling implementation changes require their own scope and agreement.

## Required owner delivery

Supply a sealed, buildable opt-in runtime bundle with:

- Exact envelope/ABI and bootstrap version, allowed profiles, quotas, native identity
  and grant closure; error and stop/close/reclaim semantics, including interrupted
  transport exclusions. Reject absent, mismatched or multiply initialized bootstrap.
- Source/object/archive/header inventories, target ABI, compiler/flags, upstream
  terms and patches, SDK/CRT/libc hashes and complete reproducible private recipe.
  Preserve historical receipts and third-party notices; never silently revise pins.
- Explicit application versus runtime objects and symbol-provider map. Component
  receipt validation must reject missing memory adaptation even when musl supplies
  linkable symbols. Also reject stale SDK/components, duplicates and wrong profile.
- One authoritative process/FD/mask state shared with the relevant musl internals,
  documented initialization/copy/rebind/exec/finalization and no retained borrowed
  pointers. Fixed image/path policy must remain owner/application policy.
- Complete positive and semantic-negative native evidence, raw streams and cleanup,
  current regressions, linked code/stack inspection, all attempts and an isolated
  consumer example. No real-prefix installation is needed for this experiment.

The bundle may retain current proven mechanisms; it must not disguise the fixed
fixture as a generally supported runtime. Aether's current serial export is the
reference input, with the304 runtime hashes and exact accepted SDK pins retained.
Do not use an unqualified historical proposal patch or mutable sibling source.

## Consumer acceptance before promotion

| ID | Required witness | Current status |
| --- | --- | --- |
| SSDK-01 | Complete isolated component build/link, exact inputs, no host fallback; missing/mismatched/duplicate component rejection | Candidate build/native serial and seven pre-link controls pass; disposition pending |
| SSDK-02 | Application-independent bootstrap, per-process state, absent/wrong profile rejection before effects | Native null/repeated start and owner wrong-grant cases pass; complete bootstrap-scope review pending |
| SSDK-03 | Public/internal mask agreement; copy/libc TLS rebind and exec/CLOEXEC with exact identity/status/cleanup | Fresh copy/rebind/exec/cleanup workloads pass; shared-mask mechanism preserved by exact source pins, review pending |
| SSDK-04 | Descriptor aliases, EOF, memory rights and unsupported/error paths remain truthful; omitted memory component rejected before build/admission | Fresh FD/error/cleanup cases and missing-memory component rejection pass; broader memory/unsupported scope review pending |
| SSDK-05 | Accepted scripted/recovery/failed-exec/scratch/serial workloads reproduced through the new runtime boundary with matching owner controls | All five workload families pass47 distinct original cases;49 fresh executions/comparisons including bootstrap probe; disposition pending |
| SSDK-06 | Independent technical/reader findings recorded against exact sources and artifacts; no fabricated approval or release claim | Pending |

Existing private native acceptances remain valid for their exact artifacts. Static
provider checks do not replace native mutants. Unsupported general filesystem,
TTY/job control, physical hangup, signals/concurrency and interrupted-service recovery
remain explicit. SI-07's versioned bootstrap/transport, rebuilt runner/bytecount
and bounded native consumers now pass separately; [current disposition](SI07-DISPOSITION.md)
records remaining schedules and integration. These ABI22 witnesses do not promote
the ABI23 SDK candidate.

## Simplicity disposition and blocker

Stock-libc-only linkage is simpler but cannot enforce the accepted component and
native state contract. Select a bounded opt-in runtime extension with explicit
component checks; defer a generic compatibility framework. Keep current small
replay drivers and unchanged owned process helper. Their duplication has no new
runtime cost, and a common harness is unnecessary for this boundary audit. No
accepted path is removed; retiring it requires named consumers and a qualified
replacement. Broader maintained-source audit remains UL-063.

Ownership is agreed; userland implementation can proceed locally in
[the runtime experiment](../experiments/session-runtime/README.md). Promotion still
requires the sealed buildable bundle, native gates above and independent review.
This task cannot create native authority or reviewer approval locally. Full M3/R1
and release acceptance remain open.

## Implementation checkpoint — 2026-09-29

The [userland extraction](evidence/session-runtime-extraction-2026-09-29/README.md)
now supplies a sealed, self-contained private008 candidate with separated runtime/
application policy, required-component admission and identical offline rebuilt
parent/helper ELFs.49 fresh native executions and independent comparisons pass,
including all five workload families, null/repeated startup, identity and cleanup.
Seven component and eight malformed-bundle controls pass. Preserved007 recompiles
are compatibility evidence, not an advertised007 bundle. Independent technical/
reader findings and scoped SSDK-01–06 disposition remain pending; runtime ownership
and local bundle implementation no longer block. SI-07 remains a separate delivery.

### Corrected rebuild dependency selection

The [cached-module fix](evidence/session-runtime-build-imports-2026-09-29/README.md)
selects verified support-module bytes directly instead of accepting a Python caller
module cache. Fresh whole ELF equality preserves native reuse; consume the corrected
candidate seal for new builds. Earlier candidate bytes and evidence are unchanged.

### Minimum Python qualification — 2026-10-03

The [minimum-interpreter repair](evidence/session-runtime-python310-2026-10-03/README.md)
reproduces Python3.10 hashing failures, replaces both newer-only API calls with
streamed SHA256 and supplies a new sealed candidate. Python3.10.21 and3.14.7
each pass ten semantic controls and rebuild exact native-qualified parent/helper
ELFs. Cached support isolation and missing-memory pre-link rejection remain intact.
Use that candidate seal for new rebuilds; historical bundles remain immutable.
SSDK-01 gains scoped minimum/current-interpreter build evidence, not promotion
or SSDK-06 reader approval. Native sources and previously qualified outputs match.

### Maintainer review timing and continued implementation — 2026-10-03

The maintainer explicitly defers SSDK-06 reader review until later lab inspection
and directs continued coding. Preserve the incomplete review/promotion gate while
continuing local implementation/tests. The [lab-kit builder](../experiments/lab-image/README.md)
now produces a pinned bounded UEFI VM kit with a fresh independent boot witness.
This development artifact does not claim physical hardware, general POSIX/session
service or SDK release acceptance.
