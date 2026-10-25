# Scoped block I/O v1

R1-03 contract recorded before implementation, 2026-09-06. Aether owns device
and capability enforcement. A future Rust filesystem service owns filesystem
policy; sys-init selects service startup. This conformance profile is not that
service, a filesystem implementation or companion adoption.

AENBD001 uses the AENSUP01 envelope layout. Bootstrap ABI 13 supplies factory
0xa001 in RSI and block selector 0xf101 in RDX. The selector confers no authority
without a matching caller binding. This profile grants exactly physical sector 7
(one 512-byte sector), initially with read=1, write=2 and flush=4 rights. Sectors
in requests are relative: only zero is allowed. No device-selection API is added.

int 0x81, signed RAX results:

| Operation | Inputs | Success |
| --- | --- | --- |
| 0x27000 read | RDI=grant, RSI=relative sector, RDX=destination, R10=512 | 512 bytes |
| 0x27001 write | RDI=grant, RSI=relative sector, RDX=source, R10=512 | 512 bytes |
| 0x27002 flush | RDI=grant; RSI/RDX/R10=0 | 0 after device completion |
| 0x27003 move | RDI=grant, RSI=live child handle, RDX=nonzero subset of rights, R10=0 | 0; initial owner loses access |
| 0x27004 close | RDI=grant; RSI/RDX/R10=0 | 0; permanent until reboot |

Only the initial bootstrap owner can move, once. The recipient binds to an exact
slot/generation and cannot forward or widen rights. Failed moves preserve owner
and rights. Terminal/reclaimed recipients and later slot generations cannot use
the binding; there is no automatic regrant/reopen after failure. Flush affects the
device cache, not a claim of a filesystem transaction or exclusive cache scope.

Error order: wrong caller/selector -13, closed -9, then operation authority (-13),
invalid sector/length/reserved fields -22, invalid buffer -14. Invalid/stale/terminal
move target -9; zero/unknown rights -22. Validate every byte of the 512-byte user
span before any DMA or user-buffer modification. Reads require writable mappings;
writes readable mappings. Integer overflow rejects. No user pointer enters a device
descriptor. User buffers remain untouched on preflight rejection.

One BSP operation runs with interrupts disabled, copying via a 512-byte kernel
stack buffer and the driver's static DMA buffer. DMA completion precedes return,
so caller teardown cannot overlap it. Driver timeout/error/invalid completion
halts the profile with DMA memory retained; no successful partial write, retry,
error recovery or quiescence/reuse claim. There is no allocation, new queue,
interrupt handler, cross-core access or general asynchronous service yet.

Pre-implementation tests: write/flush then read in a fresh VM; read-only attenuation;
wrong owner/selector, missing rights, stale/terminal targets, invalid sectors,
lengths, read-only/unmapped/overflowing buffers; close, actual recipient fault and
replacement denial. Whole-disk host checks exclude writes outside sector 7. A
broken grant-generation control must fail. Preserve old hardware, console and
boot regressions. New marker: AETHER NATIVE BLOCK PASS; old markers unchanged.

Run:

```sh
python3 scripts/block_smoke.py --native --libc-build <strict-sdk> --tools-lock <pinned-tools.json>
```

 Only newly created disposable disks are accepted. No shared
standard, package/service policy or consumer pin changes. See STATE for evidence.

Five final native cases pass, including retained-buffer rejection and recipient
fault followed by slot reuse. The generation-omission control is caught at
supervisor 844/reclaimed 2; final code is restored. See
[evidence](evidence/native-block-2026-09-06/README.md) for all attempts and hardware/
console/boot regressions. This is a one-sector producer experiment, not consumer
adoption or a filesystem-sized volume interface.

## Region grants v2 (experimental)

The opt-in [storage channel profile](OPENZFS-FEASIBILITY.md#storage-connection-admission-contract--2026-10-18)
`AENBD003`/ABI25 retains these region operations and rights, adding admission-bound
byte channels. It requires `native-service-channel`; `AENBD002`/ABI14 is unchanged.

The private [ZPL writer controller preparation](OPENZFS-FEASIBILITY.md#bounded-writer-controller-preparation-contract--2026-10-18)
also reuses AENBD002/ABI14: its selected supervisor requests sector8/count2097152/
rights7 for the first engine generation. The default namespace reader keeps
rights1. This is an explicit bootstrap delegation through the same enforcing
operation, not a new kernel grant profile or a public WRITE API. Its build-only
gate remains closed until the paired native experiment enforces the matching
reader and stopped-media prerequisites.

The separately selected [modified-reader preparation](OPENZFS-FEASIBILITY.md#modified-zpl-reader-preparation-contract--2026-10-18)
requests the same region with READ1 through ABI14 and observes the loaded pool TXG,
not an assigned application transaction. Its build-only selector accepts no user
disk or guest launch. Qualified writer-stop evidence, sealed media identity and
fresh-VM whole-file/metadata readback remain prerequisites for actual integration.

AENBD002 / ABI 14 keeps the envelope layout and grants the bootstrap owner the
whole discovered disk (512-byte sectors). V1 retains physical sector 7 only.
Existing one-hop move may transfer the whole current region with reduced rights.
New operations exist only in v2:

- 0x27005 move-region: RDI=grant, RSI=live child, RDX=readable 24-byte record,
  R10=24. The little-endian u64 fields are relative start, sector count and rights.
  Require nonempty in-bounds region and nonzero subset of current rights. Only
  bootstrap can move, once. Copy/validate the whole record and target before
  changing ownership, base, count or rights. No user pointer is retained.
- 0x27006 query: RDI=grant, RSI=writable 32-byte output, RDX=32, R10=0. Return 0
  after writing four little-endian u64 fields: sector size (512), granted count,
  rights, reserved zero. No physical start is exposed. Every live grant may query;
  query is not device authority. Invalid output spans remain untouched.

Read/write sectors are relative to the current region. Check relative<count
before adding the kernel-owned base. Region validation uses subtraction to avoid
overflow. After owner/closed checks, move permission precedes length/buffer/record/
target validation; lengths/reserved/ranges/rights return -22, pointers -14 and
invalid/stale/terminal target -9. Failed calls leave the old grant unchanged.
Query and transfer copy at most 32/24 bytes; no new pool, DMA layout, concurrent
caller, recovery mechanism or shared standard. Existing lifetime limits apply.

Requirement: meaningful disk regions usable by a future Rust storage service,
without allowing a service to address outside its delegated volume. Aether owns
native enforcement; volume selection and filesystem policy remain userland/boot
owner work. Test a 16-MiB disposable disk with an 8-MiB region, seeded first/middle/
last sectors, writes/flush/reboot, readonly attenuation, invalid metadata buffers,
zero/overflow/past-end transfer records, failed-transfer ownership, and replacement
query/I/O denial. Compare the entire disk. Retain all attempts and old profiles.
Run block_smoke.py --native --regions with the same explicit SDK inputs. No mounted
filesystem, partition parser or mature-engine port follows from this experiment.


V2 passes the five-case target suite plus the existing v1/hardware/console/boot
regressions. An intentionally omitted region base fails at the expected data
check; the original implementation was restored before final qualification.
[Retained evidence](evidence/block-region-2026-09-06/README.md) includes all attempts
and final source hashes. Producer evidence is separate from consumer adoption.

```sh
python3 scripts/block_smoke.py --native --regions --libc-build <strict-sdk> --tools-lock <pinned-tools.json>
```

## Rust transport consumer (experimental)

Requirement: exercise the existing ABI 14 grant from a Rust-owned native task and
provide a small checked byte-I/O component for the future filesystem adapter.
Aether owns this producer-side experiment. Production VFS/POSIX ownership remains
unassigned; no sys-init or pkg-mgr policy is implemented here. No new kernel ABI,
shared standard, library dependency or filesystem engine is introduced.

`user/storage/block.rs` queries the grant and expose explicit read/write/flush/
close operations. Nonempty I/O is sector-aligned and bounded to 4096 bytes per
call; the entire region/length/rights request is checked before its first sector.
The kernel remains the enforcing authority. The adapter allocates nothing and
retains no caller buffer: Rust borrows span synchronous copied native calls.
A multi-sector call is sequential, not atomic. On failure report the confirmed
prefix and cause; never replay. Unexpected native completion poisons the adapter,
with the current sector outcome unknown. Flush completion retains the existing
VM-cache assumptions and is not a filesystem durable-transaction guarantee.

Build the Rust worker as a no_std, panic-abort static library, linked to the
already pinned strict-musl startup and minimal C TLS witness. C owns startup/TLS;
Rust owns transport and workload. A mapped Rust slice remains live during each
interrupt; native register clobbers and mutable-buffer aliasing are explicit.
No new heap, threads, async queue, FFI engine callback or service protocol.

Before code, selected acceptance: the five existing region cases using a Rust
worker, including multi-sector reads, denied/unaligned/oversized/overflowing calls,
unchanged buffers on local preflight rejection, close and recipient fault/reuse.
Host full-disk checks and fresh-VM reads remain authoritative. A deliberately wrong
byte-to-sector conversion must fail the unchanged guest data check. Preserve the C
region suite and host/standards/format checks. This is a transport component in a
native task, not a mounted filesystem or client-facing storage service.


Run the Rust task with the same explicitly pinned SDK and tool lock:

```sh
python3 scripts/block_smoke.py --native --regions --rust-worker --libc-build <strict-sdk> --tools-lock <pinned-tools.json>
```

The five Rust cases pass, including multi-sector write and a maximum-size read.
An aligned 8192-byte request checks the transfer ceiling independently of alignment;
invalid reads retain their buffer sentinel. A second wrapper around the same grant
observes native -9 after consuming close, demonstrating that cached metadata does
not retain authority. Two wrong read-offset implementations reject at the exact
native read/data checks. [Evidence](evidence/rust-block-2026-09-06/README.md) retains
all attempts and regressions. The unexpected-completion poisoning and nonzero
prefix failure branches still need injection evidence; current native device
uncertainty halts rather than returning a recoverable error. No automatic close,
regrant, recovery or transaction semantics are added by the Rust wrapper.

## Large-service region composition scope — 2026-10-06

Before implementation: the initialized empty OpenZFS candidate has no usable
volume in its AENSUP01 service-memory profile. First qualify the existing ABI14
region operations with the same8192-page service backing and small peers. A new
explicit build selection permits AENBD002 only when service-memory is selected;
default AENSUP01 service-memory and legacy region-v2 profiles remain unchanged.
This composes existing native primitives, not the engine or maintained pthread
runtime, and creates no new block operations, ownership table or service protocol.

Keep bootstrap transfer, single authoritative recipient, exact slot/generation,
attenuation, pointer/range validation and permanent close/replacement denial.
Transfer never becomes a restart grant factory. Current synchronous DMA completion
and fail-stop uncertainty retain their limits. The harness accepts only a fresh
owned16MiB disk; writes are limited to the existing delegated8MiB region, with
complete host readback/canaries and a fresh VM. No path can select a real disk.

SE-01–05: reusing ABI14, its existing C/Rust clients and bounded physical backing
is smaller than introducing a volume broker, regrant policy or new envelope now.
One opt-in profile guard is justified by the next engine-volume prerequisite.
Select the five current Rust region cases under large backing, the unchanged
small region suite and affected service-runtime regression; run build-policy,
format and workflow checks. Record separate evidence; this does not measure an
engine pool, ARC growth,82 worker load or maintained runtime/block composition.
UTC policy remains outside the kernel; Aether-userland is the assigned shared
runtime owner. Raw clock source and maintained UTC qualification remain required.

Run the scoped composition with the existing guarded base (not the supplemental
pthread archive):

```sh
python3 scripts/block_smoke.py --native --regions --rust-worker --service-memory --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

Six cases pass: write, fresh-VM verify, read-only attenuation, actual recipient
fault/replacement denial, corrupt-data rejection and omitted-profile rejection
before any disk change. Existing five small-region Rust cases and the maintained
service-runtime normal workload pass on final kernel inputs. Four client ELFs and
four supervisor images are byte-identical between large and small region runs.
The actual large profile admits24 image/stack pages with8168 remaining; this is
the Rust transport fixture, not engine/heap/worker fit. Full integration214 host
checks, Zig/pins, scoped formatting and guarded240-member SDK seal pass. See the
[compact result](evidence/service-block-profile-2026-10-06.json). Generated outputs
are disposed after each run. Engine vdev binding and maintained runtime/block
composition remain before pool operations; no automatic grant reissue is added.

## Maintained runtime and volume scope — 2026-10-06

Requirement before code: execute the sealed maintained pthread runtime with the
already qualified8192-page/82-worker region-v2 profile. One supervisor explicitly
transfers one8MiB region to slot0/generation1; its initial thread and real pthreads
read through the native boundary. Write/flush and fresh-VM readback precede engine
vdev binding. Peers/replacements receive no grant and must reject; close is final.
No kernel operation, grant table, quota, automatic regrant, UTC, SDK or pin change.

Private startup ordering is explicit: child launch can run before the supervisor
transfers. Only the expected first fixture generation may await its declared binding
by query plus existing native monotonic1ms parks, retaining one1s deadline. Other
owners check denial immediately. Missing binding cannot become success. This is a
bounded private launch handshake, not a new production startup/configuration API.
The token label0xf101 confers no authority; exact native slot/generation enforces
possession. Sys-init retains production supervision/launch policy. One copied
transfer record is borrowed only for the synchronous call, then discarded.

The existing source-bound runtime probe checks full81/one application capacity,
charged reaper, condition/mutex/TSD/join cleanup and final retirement. Insert only
volume validation and a512-byte reads in the first real worker and one selected full-cohort worker after timeout/relock; direct
calls preserve native errors and do not invent POSIX file/path semantics. Existing
synchronous IF=0 transport serializes device I/O; there is no user-space DMA pointer
or asynchronous completion. Main closes only after all application workers join.
Replacement generation must not inherit the old volume even before/after close.

Forbidden outcomes: pre-transfer unauthorized success, grant expansion, peer or
replacement I/O, write/flush with read-only rights, dirty sectors outside the region,
corrupt input treated as success, surviving workers or reuse before terminal/reclaim.
Run one fresh owned16MiB disk: write exactly its first delegated sector, flush,
read back across a new VM; full host comparisons check every byte/canary. Separate
read-only/corrupt disks remain unchanged. Retain failed attempts and compact hashes;
never accept a user disk or retain generated disk/image/build bundles.

Simpler alternative: keep independent runtime and region tests. It cannot establish
composition under real thread/backing/clock lifetimes. Reuse existing grants, parks,
worker probe and supervisor lifecycle; only a private binding witness is added.
The first combined run misrouted native read arguments and rejected840 before
writes. Correcting that exposed startup-budget exhaustion813 when every worker
read synchronously. Representative worker reads preserve the existing budgets;
full-cohort runtime capacity is checked independently of I/O throughput. No
production libc fork, VFS, vdev policy or persistent pool is introduced. UTC
and actual checked engine vdev/timestamp consumers remain subsequent work.

Command (four fresh-VM cases; existing runtime/base remain sealed):

```sh
python3 -m unittest discover -s tests -p test_service_block_runtime.py
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --block-region
```

For iteration select `--case block-write`, `--case block-readonly` or
`--case block-corrupt`. `block-verify` requires the full write/verify sequence;
the runner must reuse the actual disk from the preceding VM, not synthesize
persisted data from its expected-output oracle. No external disk argument exists.

## Page-fragment copy scope — 2026-10-07

The actual open-probe trace locates long successful8192-byte provider calls. Each
provider transfers16 sectors; native blockOperation currently resolves the same
page records for every byte during full-buffer validation and copying. Replace
only that sector's repeated lookup with at most two checked page fragments. This
removes redundant linear scans without changing block ABI, rights, sector size,
partial-progress semantics, DMA ownership, queues or scheduling. It is a concrete
cost reduction, not yet attribution of a previous timeout or a latency guarantee.

Check the entire512-byte user span and its required access before device I/O or
caller-visible writes. IF=0 keeps the owner, page records, mappings and backing
stable from validation through synchronous DMA and copying. Captured fragments
are private stack borrows and never escape blockOperation; page-boundary splitting
handles noncontiguous backing. Copies use only the private512-byte kernel buffer,
which cannot alias caller backing. Read destinations need writable mappings;
write sources need readable mappings. Keep null/overflow/unmapped/readonly/region/
rights/revocation denials and validation-before-effects. No global lookup cache,
new mapping API, authority shortcut or changes to the general byte resolver.

Add a bounded C native witness for a sector crossing a real4KiB page boundary,
intact adjacent guards, same-data writeback, and mapped-first/unmapped-second
read/write rejection without mutation. Compose it with existing worker fixtures;
use existing native C and Rust region/service-memory suites, including fresh-VM
verification, read-only rights, corrupt data, fault/replacement and wrong-profile
controls. Run the full host checkpoint once because this changes an unsafe kernel
copy boundary, then physical target group and revoked ZIO as direct large-owner
consumers. Root/default engine bytes and released pins remain unchanged; no sibling
modification or driver/pool/persistence claim. Freeze sources and dispose outputs.

SE-01–05: use bounded stack fragments instead of repeated scans; a global mapping
index/cache would add ownership and invalidation complexity not required here.
Two fragments suffice for the existing sector ABI. No new service, dependency,
shared state or production trace interface. This scoped change removes redundant
validation work while preserving complete access checks and existing failure order.

Result:17 native block cases pass across legacy C, region C/service backing and
Rust region/service backing. C cross-page/guard/writeback and second-page/protected
output denials pass without buffer/media mutation. Fresh-VM verification, rights,
close, fault/replacement, corrupt and wrong-profile controls remain exact. Physical
ZIO group and revoked direct consumers pass; paired open checkpoint engines stay
identical while provider clock context shortens substantially.238 host tests/Zig/
pins pass. See [scope/result](OPENZFS-FEASIBILITY.md#original-open-probe-observation-scope--2026-10-07)
for commands, compact retention and limits. No all-schedule latency, physical-device,
DMA-quiescence, production-service or persistence claim is made.
