# Native lifecycle fixture ABI v1

Aether-owned, bounded x86_64 single-core conformance profile. This is an interface
for a separately supplied supervisor image, not a general loader, init policy,
POSIX ABI, or completed sys-init integration. Sys-init chooses its own language
and whether this profile meets its experiment requirements.

## Image and bootstrap

A third ordered boot module, `lifecycle.bin`, carries a 32-byte little-endian
header followed by 1–4096 immutable code/constant bytes, with no trailing bytes:
magic bytes `AELIFE01`, u32 ABI=1, u32 role=1 (supervisor), u64 entry=0x400000,
u32 code length, u32 reserved=0. Reject every mismatch before execution. This
header identifies a profile; it is not a signature or source provenance proof.

Map code RX at 0x400000 and one zeroed RW/NX stack at 0x800000; initial RSP is
0x800ff8, interrupts enabled, RDI=1 (ABI), RSI=factory handle, RDX=1 (worker quota),
RCX=4096 (page size). No argv/env, filesystem, console handle, shared user memory,
FP/SIMD, device grant, or arbitrary program selection is supplied. The bootloader
and selected module bytes remain trusted bootstrap inputs. Build traces/hashes
must pin all matching kernel and module artifacts for a companion experiment.

## Invocation and authority

int 0x80: RAX operation, RDI handle, RSI value; returns RAX status, RDX result.
Other general registers are preserved. Status: 0 success, 1 invalid handle/type/
identity/operation, 2 denied rights, 3 exhausted quota, 6 invalid lifecycle state.
Full/Empty (4/5) belong to endpoint operations, not this factory profile.

The caller has one eight-slot generational capability table. Factory rights:
allocate=1, create=2, derive=4, revoke=8, observe=16, acknowledge=32. Memory:
attach=1, release=2, derive=4, revoke=8. Task: start=1, destroy=2, derive=4,
revoke=8, inspect=16. A generation handle is holder-scoped authority, not an
instance ID or a service name. Slot generations and instance generations never
wrap. No transfer/multiple-holder observation exists in v1.

| Operation | Required authority | Result/effect |
| --- | --- | --- |
| 3 derive; 4 revoke; 5 close | Existing local capability rules | Attenuate same-holder rights, revoke descendants, close leaf |
| 10 allocate | Factory allocate | One 8 KiB code/stack backing bundle; returns memory handle |
| 11 create | Factory create, memory attach in RSI | Instantiate the fixed worker; returns task handle |
| 12 start | Task start | Make the created worker runnable once |
| 13 inspect | Task inspect | 0 pending, 1 exited, 2 faulted |
| 14 destroy | Task destroy | Forced local stop if needed, unmap/flush, invalidate task handles, detach backing |
| 15 release | Memory release | Invalidate memory handles, zero/verify both pages, then free backing |
| 20 yield | Caller execution only | Yield local timeslice; not a clock or service readiness API |
| 30 ABI query | Factory observe | 1 |
| 31 instance ID | Task inspect | Nonzero boot-local worker generation |
| 34 terminal instance | Factory observe | Retained generation, or 0 if no record |
| 35 terminal reason | Factory observe | 0 none, 1 exited, 2 page fault, 3 forced stop |
| 36 terminal detail | Factory observe | Exit status, page-fault vector (14), or 0 for forced stop |
| 37 acknowledge | Factory acknowledge; generation in RSI | Consume matching terminal record only after task destruction and memory release |
| 0 conformance completion | Caller execution only; RSI=100 | Finish the bounded harness after its required trace; no resource authority |

One immutable terminal record belongs to the factory's supervisor holder. Normal
exit/fault publishes it before descheduling; forced destruction publishes a stop
record only when no terminal result already exists. Repeated reads are stable.
Destruction invalidates task references but preserves the record; release also
preserves it. Wrong-generation acknowledgment is Invalid; acknowledgment while
task/backing remain is Busy. Allocation after release remains Busy until the
record is acknowledged. An exhausted or rejected operation leaves prior state
intact. There is no observer queue, durable log, or automatic record overwrite.

## Fixed worker and acceptance trace

The selected worker is the immutable protection fixture, not a caller-selected
program. Generations 1–9 follow the existing conformance workload: one normal
exit (status 110), seven reads of the previous stack address causing faults, then
one dirty live worker that yields until explicitly destroyed. Virtual stacks
alternate; the worker checks clean backing and dirties it before each result.
The supervisor must perform all nine cycles and check identity, authority,
quota, terminal retention, stale references and acknowledgment. This finite
workload is a deliberate profile limit, not a general service restart policy.

The kernel verifies nine releases/acknowledgments, seven faults, one normal exit,
one live stop, and no outstanding task/backing/record before emitting
`AETHER LIFECYCLE V1 PASS`. The supervisor is a separately replaceable conformance
client in this repository; it is not sys-init. A sys-init-owned component must
actually consume the seam before cross-project runtime integration is claimed.

Cleanup remains single-CPU: remove runnable state and mappings, reload supervisor
CR3 with non-global pages/no PCID, invalidate task references, detach, then
invalidate memory references and zero/verify before freeing. No AP uses these
pages. A terminal record is evidence of task outcome, not permission to reuse
memory before cleanup.

A 1,000-PIT-interrupt harness watchdog bounds stalling; it is not a calibrated
user deadline API. Supervisor exception or failed completion panics and halts the
boot CPU before AP release; resources remain reserved, with no recovery or
orphan adoption claim. Required readiness, cooperative shutdown, multithreaded
services, remote grants, SMP restart, DMA and persistent recovery are unsupported.

## Consumer commands

`zig build` compiles the default Rust conformance client and packs its header.
A separately authored raw image can use the shared fixed entry/linker layout:

```sh
python3 scripts/lifecycle.py pack SUPERVISOR_RAW SUPERVISOR_ENVELOPE
zig build smoke -Dsmp=false -Dlifecycle-image=SUPERVISOR_ENVELOPE -p zig-out/companion-lifecycle
```

The explicit override never falls back to cached/default client bytes. The
one-core smoke requires the versioned lifecycle marker. Default two-core smoke
continues through M3 and display acceptance. `-Dbad-lifecycle-abi=true`,
`-Dfail-lifecycle-supervisor=true`, and `-Ddrop-terminal-test=true` are negative
checks; use separate output prefixes. Reject combining an external image with
built-in client fault flags. No companion pause/acceptance state is changed by
these commands or by the existence of this document.
