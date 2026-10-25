# Larger-owner memory scans

Status: private producer qualification passes, 2026-10-04.
[Before-code scope](evidence/native-service-scans-2026-10-04/contract.md) follows
the observed larger-profile timeout. Only the 8192-capacity sliced arena uses a
1024-byte temporary bitmap for occupancy/coverage and a constant-size record
cursor for protect/unmap commit. No persistent index, allocator, authority or ABI
is introduced. Existing typed 128/2048 algorithm and commit order stay unchanged.

Metadata addresses must be aligned and within the actual owner bounds to index
the temporary set. Map includes immutable occupancy; range requires anonymous
coverage and keeps pin/error/preflight ordering. Owner-serialized commits traverse
unique matching records once and may mutate only visited records. User PTE detach,
kernel-only alias write restoration, CR3 flush, zero verification and quota return
retain their existing order. The required exception stack remains 64 KiB.

Map/range work is proportional to owner records plus scanned arena/request pages;
commit visits at most the owner records, with table selection bounded by 32.
Zeroing/verification still scales with requested payload. This is an algorithmic
bound, not wall-clock WCET, a stack high-water proof or scheduling assurance.
Actual operation latency, larger live-worker admission, native musl TCB/stack
demand, full-engine lifecycle, independent reader/SDK adoption and R1 remain open.
Run the recorded recipes and `zig build test`; frozen results retain every attempt.

44 fresh target cases pass: 25 maintained memory, seven M4, ten larger-owner
and two thread storage. Full 137 Python/Zig/Rust/pin/workflow and 15 memory model
tests pass. Removing coverage validation fails the exact anonymous-hole witness.
The big-image case again performs full allocation/protection/zero/reuse in all
three generations, under the unchanged 30-second watchdog. Its recorded case
interval is about 11 seconds including compilation/build; that is an observed
host/fixture interval, not kernel syscall latency or WCET. Prior pair/origin/reuse/
entropy coverage is historical only, bound to unchanged runtime bodies outside
this private memory operation. No expanded worker or production scheduling claim.
