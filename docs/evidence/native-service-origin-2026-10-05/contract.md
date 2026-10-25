# Real musl worker-origin creation and concurrent preflight

Before-code scope,2026-10-05. R1-03 needs actual musl worker-origin thread creation,
not just bare native children. Aether owns a private producer conformance witness;
production libc/runtime remains userland-owned. No kernel, public ABI/SDK, quota,
sibling, released standards or pin changes. Accepted VM/musl/identity/clock designs
and current eager owner-local storage remain authoritative.

Requirement: two joinable service creators enter actual musl pthread_create
preflight concurrently and create40 detached peers each. They count within82 live
records. Small peers use one joinable creator and one detached peer; a single-
creator service variant covers81 peers. The primary creates only the creators.
An explicit preflight barrier before upstream locks establishes both calls are
in progress. Actual musl's thread-list lock serializes __clone and slot publication;
atomic used/admission counters cover concurrent preflight reads. No cleanup starts
until all creators have returned from all creation calls and all workers park.

First creator owns all detached cleanup while the primary joins it through actual
native compare-and-park. A second creator waits for cleanup completion, then the
primary joins it too. Exact saved native IDs/mappings, per-thread TLS/errno/TSD,
creator-specific signal masks and zero/stale/resource invariants remain. Atomic
publication precedes metadata reads; one record is written only under upstream
list-lock ownership, and reaping mutates it only after creation-phase completion.
Callbacks determine their published physical slot by exact current ID, rather
than assuming concurrent caller argument order matches native admission order.

Untrusted IDs or request flags confer no authority. Native clone, observe, unmap
and retire validate existing held domain grants. Running peer stack/TLS mappings
remain pinned. Stop is observed before unmap/retire; unmapped TCBs are never read.
Wrong-grant clone must return EACCES before native effects; upstream EAGAIN cleanup
must preserve failed caller output, mapping budget and admission count in the
single-creator control. Restoring parent-only admission must reject exact359;
wrong-grant creation control360, early unmap352 and omitted primary park356 must
reject by named terminal/supervisor/panic, never timeout/unrelated failure.

The fixture's fixed records remain protection-domain-local bookkeeping, not a
kernel authority table or public pthread ABI. First creator alone reaps; rejected
witness cleanup permits published peers to exit but leaves their records/mappings
allocated, then synchronizes upstream list state and reports the exact failure.
Cancellation, dynamic pthread_detach, creation overlapping retirement/reuse,
orphaned-service recovery and unbounded concurrent schedules remain unsupported.

Tests: joinable and worker-reaper regressions, concurrent and single-creator
origin, descending completion, parked stop/replacement and the four exact controls.
All82/two actual stack/TLS mappings, TSD/destructors, counted wake, failed allocation
preservation and independent parent state qualify. Use frozen180-second builds,
30-second guests/3-second teardown, retained all-attempt source/tool/SDK/recipes,
actual pinned rustc/linker hashes and full host/pins/workflow/format/link checks.
Unchanged older native runtime evidence may bind identical source bytes only as
historical coverage. Document reference, workflow, STATE and R1 roadmap.

Simplicity: phased batch creation and one cleanup owner suffice for required
worker-origin/concurrent-preflight evidence. Kernel RPC creation or a new generic
registry/reaper service would add authority and lifetime complexity without a
current need. Reuse upstream locking and existing native primitives; atomics only
cover genuinely shared admission/preflight/publication state. No production path
is removed now. This trial does not select production reaper placement, admit82
detached engine workers, measure engine peak or establish dynamic creation/reuse.

Before final retry: attempt1 passes both old joinable/reaper regressions, then
fails compiling the new origin case because a negative-only clone result variable
was declared for every origin build. Guard that variable with DENIED_CREATE;
retain the failed receipt/source. Also assert the actual current musl list-lock
owner at clone publication and remove the unused copied observation-denial branch.
The lock's libc TID is private bookkeeping, not native authority. Kernel grant
validation stays unchanged and all ten cases rerun on final bytes.
