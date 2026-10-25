# Native launch byte channel v1

The separate private [storage admission experiment](OPENZFS-FEASIBILITY.md#storage-connection-admission-contract--2026-10-18)
reuses these queues and holder checks in opt-in `AENBD003`/ABI25. Its operation
`0x20008` transfers a supervisor-owned empty request reader and reply writer before
the native storage image runs; auxv keys are `0xa004/0xa005`. It is not launch-v1
or a released SDK extension. Existing profiles and their auxv keys remain unchanged.

Bounded kernel mechanism for two separately launched helpers. This is not POSIX
pipe/pipe2, fork inheritance, descriptor duplication, a process service or a shell.
The userland process/FD audit requires those additional semantics and checked libc
fallbacks. Their ownership and shared requirements remain with the companion
projects and Aether-standards; this document defines only the exact kernel seam.

## Profile and authority

AENCH001 uses the same layout and limits as AENEX001. Supervisor ABI is 4, with
existing factory/image grants plus R8=channel factory grant 0xd001. Old profiles
are unchanged. One BSP-owned 32-byte channel exists at a time; its two distinct
read/write endpoint grants initially belong to the supervisor. Endpoint values
bind the channel generation and are checked against the invoking domain's owner
binding. Three generations are allowed; exhaustion never wraps.

Interrupt 0x81, signed RAX results:

| Operation | Inputs | Success |
| --- | --- | --- |
| 0x24000 create | RDI=factory; RSI/RDX/R10/R8/R9=0 | RAX=read grant, RDX=write grant |
| 0x24001 read | RDI=read grant, RSI=buffer, RDX=length; others zero | bytes read, 0 at drained EOF |
| 0x24002 write | RDI=write grant, RSI=buffer, RDX=length; others zero | bytes written |
| 0x24003 close | RDI=endpoint; other inputs zero | 0 |
| 0x23001 launch with endpoint | same as launch 0x23000, but R8=owned endpoint | fresh child handle |

Launch transfers one endpoint only after the complete launch request validates;
failed launches preserve endpoint ownership. The supervisor loses that endpoint.
Child auxv key 0xa001 supplies it. No duplication, implicit inheritance or reverse
transfer is supported. Ordinary 0x23000 still launches without an endpoint.

Invalid/missing/stale/foreign authority returns EACCES before effects; wrong
direction returns EBADF. Reserved fields and lengths above 256 return EINVAL;
unreadable/unwritable buffer ranges return EFAULT. Transfers handle at most 16
bytes, validate that entire chunk before queue effects, and may return shorter
counts. Empty live reads and full writes return EAGAIN. Writer closure permits
buffered drain then EOF. Reader closure makes subsequent nonempty writes return
EPIPE, without SIGPIPE. Zero-length valid-direction requests return 0. There is
no blocking/wakeup or atomic POSIX PIPE_BUF guarantee.

Creation returns EBUSY while either endpoint remains open, ENOSPC after the third
generation. Closing is consuming and cannot report interruption while retaining
an endpoint. Exit, user fault and supervisor stop automatically close all endpoints
owned by that worker before retaining its terminal result. Both ends closed clears
all queue storage before reuse. No prior-generation endpoint survives reuse.
Supervisor death remains the existing fatal-profile limitation.

## Acceptance

A kernel-owned client must run a producer and consumer with different executable
grants, explicit endpoint transfer, ordered data and EOF. It must exercise full/
empty queues, denied directions/authority, stale endpoints, failed-launch rollback,
reader loss/EPIPE, automatic exit cleanup and fresh generation reuse. These are
mechanism tests; the userland-owned descriptor adapter has not adopted this ABI.

## Reproduce

```sh
python3 scripts/launch_smoke.py --channel \
  --libc-build /absolute/Aether-userland/build/native-c-BUILD \
  --tools-lock /absolute/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test
zig build smoke
```

This reuses the launch runner's verified strict-libc and compiler/linker inputs,
private outputs, hashes, maps and timeouts. Its help/version and exit contracts
remain unchanged. Output is under `zig-out/channel-suite-*`; incomplete evidence
is retained on failure. `native_smoke.run` reports the selected profile marker
for non-startup profiles; its original startup CLI message remains unchanged.

The producer sends 96 patterned bytes in normal/fault runs, or 16 before a
readiness notification and controlled stop. The consumer checks order and drains
to EOF. A final writer in a reused slot observes EPIPE after the supervisor closes
the fresh channel's reader. The suite then requires exhausted-generation rejection
and no remaining owned endpoint or nonzero queue storage before emitting
`AETHER NATIVE CHANNEL PASS`. Three child reclaims are required.

A wrong-count consumer expects only 16 of 96 bytes and must exit 103, followed by
supervisor result 511 before any reclaim and the exact profile-rejection panic.
An unrelated panic, boot failure or timeout cannot pass that control. Additional
positive assertions check full/empty queues, old and transferred handle denial,
wrong directions, failed-launch retention, busy-slot launch rollback, input-copy
failure without publication, and inaccessible/read-only read buffers without
consuming data. All operations run on the BSP with interrupts disabled; none
promises POSIX concurrency or signal semantics.

The existing launch, memory, frozen userland memory/descriptor and default SMP
suites remain separate regression witnesses. A passing consumer regression does
not mean the userland adapter has adopted this new channel profile.

[Retained results](evidence/native-channel-2026-09-05/README.md): four channel
cases, five launch cases, eleven memory cases, twelve frozen userland consumer
cases, host/standards checks and default two-core/framebuffer acceptance pass.

## Private storage primary waits — 2026-10-20

AENBD004/ABI26 adds wait0x24004 to the explicitly selected storage channel profile.
Inputs: owned endpoint in RDI; all other argument registers zero. It returns0 as a
level-readiness hint, EACCES for foreign/stale authority, EINVAL for reserved inputs
or a storage helper caller. It transfers no bytes and retains no pointer. The
primary context alone parks; storage helpers continue through existing nextContext.
Wake completes only the primary saved frame once. Close makes the endpoint ready
so a subsequent transfer observes EOF/EPIPE; stop/reset cancels the registration.
AENBD003/ABI25 retains ENOSYS and the existing session profile is unchanged.

Read-only integration is selected with `--namespace-wait --namespace-ipc` in the
service-runtime runner; exact command is in NATIVE-C. It requires the fixed BSP
namespace import/cleanup profile and all existing bounds. Its numeric diagnostic
`NATIVE STORAGE WAIT slot=N generation=G phase=park|wake status=S` is opt-in;
supervisor slot2 generation0 is permanent, storage slot0 generations1..3 are
instance-scoped. No grant or pointer is printed. The conformance oracle requires
balanced successful registrations/completions as well as the unchanged file,
media, authority and cleanup checks. Full worker scheduling, close/revoke/reset
and primary-frame semantics also have host execution/compiling omission controls.
This is not permission for arbitrary helper waits or an operational filesystem ABI.


The2026-10-20 readonly native qualification passes50 paired park/wake events,
full original file/media and all three-generation cleanup/authority guards.
Supervisor identity is slot2/generation0 for this storage envelope. An initial
slot3 checker error and its missing final media coverage remain a failed attempt;
focused repair then a separately invoked exact-engine/controller qualification
passes. See STATE's compact receipts. This does not qualify writable service
adoption, operational lifecycle/idle or all helper races.


## Page-fragment channel validation — 2026-10-20

The fixed<=16-byte transfer validates each touched page once through the original
owner-local `byte` predicate. A private two-fragment view covers at most two pages;
backing need not be contiguous. The complete requested chunk validates before any
queue or user-buffer effect, including short transfers, empty/full queues and
closure. Read destinations require writable user mappings; send sources require
readable user mappings. Direction/holder/reserved/error precedence and zero-length
behavior are unchanged. IF=0 spans validation and effects; no slice survives this
syscall. There is no mapping cache, new static state, grant, ABI or resource limit.

```sh
python3 -B -m unittest discover -s tests -p test_native_channel_copy.py -v
```

The test executes the actual lookup, two-fragment helper and syscall tail with
real Channel/Stream state: every chunk/page boundary, permuted backing, holes,
flags, stale/foreign/direction/reserved/overflow, full validation before effects,
short/empty/full/closure and exact one/two lookup counts. Four compiling omissions
must fail for second-page write rights, backing contiguity, premature queue effects
and redundant lookup bounds. Host lookup counts are not wall-clock performance
or target qualification; current native results and failures remain in STATE.
