# OpenZFS native capacity reassessment — 2026-09-07

**The qualified host profile does not fit the current native fixture.** Keep the
mature C engine evaluation and Rust service direction, but do not increase kernel
arrays or select a filesystem memory budget from these Linux observations. The
next executable step is a private static musl/platform build audit, described below.

This is an offline analysis of the sealed file-vdev experiment, not a new engine
run. All 88 preceding packet files were verified before use. All 44 sample records
were reconciled; numerical summaries below use ten measured one-worker processes
per CPU view, excluding warmups. Each measured process has three engine lifecycles.
[analysis.json](analysis.json) retains every selected sample and min/median/
nearest-rank p95/max. [analyze.py](analyze.py) is a retained one-off recipe, invoked
from the repository root; it is not a new supported developer entry point.

| Observation | Modeled one CPU | Host view: 9 CPUs |
| --- | ---: | ---: |
| Peak registered workers | 82 | 146 |
| Concurrent requested worker stacks | 21,495,808 B (20.5 MiB) | 38,273,024 B (36.5 MiB) |
| Concurrent requested guards | 335,872 B | 598,016 B |
| Lifetime successful creates | 281 | 473 |
| Creates at first kernel_init return | 10 | 13 |

Each row is constant across its ten measured processes, so median, p95 and maximum
agree. The caller/main context is additional to observed created workers. Outer
pthread cleanup closes these intervals before final TLS destruction/native stop;
zero registered workers does not prove native stack reuse is safe. Guard requests
are address-space requirements, not automatically backed physical pages. Cumulative
creates must not be used as a simultaneous slot count.

## Source-backed native limits

The exact reviewed source files are copied under inputs/ and hashed in analysis.json.
These limits belong to opt-in conformance profiles, not a production service API.

| Boundary | Current implementation | Consequence |
| --- | --- | --- |
| Live children | native_c.zig State.children permits two with native_thread_pair, otherwise one | Even startup's ten creates exceed current admission; the full storage profile needs a wider runtime design. |
| Lifetime admissions | native_execution.zig child_admission_limit = 4; retire does not refill it | Slot reuse alone cannot run 281 creates. Preserve nonrepeating generation-bound IDs and exact-stop reaping when designing reusable admission. |
| Creation caller | native_c.zig rejects create from s.on_child before publication | Raising the slot count alone does not qualify engine worker-originated creation. Audit creation call contexts; do not silently delegate authority or route blocking work through a deadlocked parent. |
| Per-domain backing | native_c.zig shares arena.page_count backing/pages across addPage image loading and arena.map | Large mode has 2,048 × 4,096 = 8 MiB total image/primary stack/anonymous backing, not a separate 8 MiB heap. Worker stacks alone exceed it. Default is 128 pages. |
| Loader | native_elf.zig admits static x86_64 ET_EXEC, bounded segments/TLS/permissions; large file input is 8 MiB | The retained Linux PIE/dynamic dependencies are not loadable. Debug file size and mapped image size are separate from runtime allocation. |
| Address/table geometry | native_memory.zig has 32 page-table reservations; native_launch and native_c validate fixed geometry/aliases | More backing requires independent layout, alias, table, cleanup and overflow review, not a constant-only change. |

The prior x86 Linux executable's 1,287 mapped pages are historical build evidence,
not the size of a native musl rebuild. Do not subtract that number from 8 MiB to
claim native free space. The present taskq witness proves two separate queues and
safe reaping within existing grants; it is not an engine launch profile.

## What the retained measurements cannot size

The observer's mallinfo2 samples include libc and observer allocations and miss
activity between sampled events. They are not allocation-complete engine peaks.
For the modeled one-CPU view, sampled used-byte maxima range 4,616,432–4,622,352;
sampled mmap-byte maxima are 2,703,360, and arena-byte maxima range
18,456,576–19,894,272. Host-view values are in analysis.json. Do not add independent
maxima or count arena reservation and its used subset twice. None is a musl heap
budget, measured stack high-water, RSS or a maximum under storage pressure.

First-aggregate-peak role attribution reconciles to each recorded total. ZIO roles
account for 55 workers at that point in the one-CPU samples; other queues still
need independent progress. Individual role maxima are not added to invent a peak.
The host view can reach its first peak with a different role composition. The
one-CPU view changes discovery, not max_ncpus or all internal queue policies.
No further queue merging or blind worker reductions are selected by this review.

## Next executable step and gates

1. In a fresh private output root, attempt the selected libzpool source closure
   against the pinned native musl SDK, starting with kernel_init/kernel_fini and
   the qualified system/delay, ARC and file-worker selections. Retain compiler
   failures and unresolved symbols as named platform-port work. Separate engine
   dependencies from the Linux-only host fixture and observer. Preserve CDDL
   notices, original archives and SDK bytes; no sibling edits or pin changes.
2. Classify each missing boundary: already-qualified native mechanism, private
   C/musl adaptation, or absent capability-backed facility. Do not fabricate
   successful file/flush/clock/entropy/discovery operations to obtain a link. No
   Linux ABI emulation, global privilege or glibc pthread layout substitution.
   A linked object/image is build evidence only; native execution needs a contract.
3. Use the actual rebuilt image and bounded allocation/stack evidence to propose
   startup-only memory and owner-local thread admission. Specify required-resource
   failure, caller authority, generation exhaustion, wait/reap lifetime and full
   cleanup before selecting numeric limits. Ten host startup creates are a demand
   observation, not permission to hard-code ten as a native maximum.
4. Qualify startup/fini and restart before owned-volume storage. Storage additionally
   needs grant-bound I/O, honest flush ordering/uncertain outcomes, namespace and
   Rust service composition. Host file-vdev success does not replace this work.

This ordering addresses build/runtime compatibility before a large kernel capacity
change. Full pressure/soak, native stack/allocator peaks, native service admission,
independent consumer review and shell/package integration remain open. No new
cross-project contract, release decision or post-R1 feature is introduced.

## Checks and reproducibility

Run `python3 docs/evidence/openzfs-native-capacity-2026-09-07/analyze.py` from the
root only when intentionally reproducing into a fresh copy of this packet. It
verifies the preceding manifest, checks populations/profile attribution/cleanup,
and records three exact semantic counterexample rejections: missing sample,
wrong aggregate count and substituted file profile. It never runs retained
container commands. Source snapshots bind this review to the current dirty
working tree; they are not an independent committed build.

Host tests, offline pins/workflow, local links and whitespace checks are recorded
with this packet. No native code changes or new QEMU claims. Existing evidence,
release bytes, consumer pins and sibling repositories remain unchanged.
