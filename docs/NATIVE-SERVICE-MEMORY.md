# One larger native service memory owner

Status: private producer qualification passes, 2026-10-04.
`-Dnative-service-memory=true` requires native external backing, large memory and
large image options. Only AENSUP01 is accepted, before reservation. No public
ABI or general VM mapping API is introduced. Default and prior external profiles
retain their existing embedded metadata, backing view types and quotas.

One BSP-owned retained 64 MiB pool has an 8192-page (32 MiB) partition for domain
0 and three 128-page partitions. Supervisor domain 2 stays small; domain 1 can
run a small peer, and domain 3 remains unused here. The tail is not granted.
Each State remains its metadata/grant/context/generation owner. Only this profile
uses bounded payload/metadata slices; one 8192-record static array and three
128-record arrays stay off the stack. Reset reconstructs both views from the
checked domain identity, then clears only that owner's metadata. No caller
pointer, physical address or numeric quota conveys authority.

The 32 MiB choice is a trial budget beyond the older 8 MiB limit, informed by
recorded image/worker-stack lower bounds. It is not an observed native allocation
peak, physical-memory sysconf value or full OpenZFS budget. Existing 32 leaf tables
remain bounded; 32 MiB contiguous anonymous memory needs 16, in addition to loader/
stack spans. Sparse table exhaustion remains an atomic error. No metadata or
payload array grows across every domain. Existing live/lifetime child limits,
exact-ID retirement, context pins, masks and entropy lifetimes remain unchanged.

Queries, arena and thread stack/TLS validation use the actual owner's metadata
length. Pure plans keep the old typed 128/2048 API; only the 8192-capacity profile
borrows slices and rejects empty/oversized views. Caller resource limits cannot
expand a small view. Plans remain 16 bytes, and the sliced free cursor is at most
40 bytes. Owner metadata stays stable through IF-clear preflight and commit.

Use [recorded recipes and scope](evidence/native-service-memory-2026-10-04/README.md)
with pinned offline tools/SDK, then `zig build test`. Required target selection
includes complete embedded/external memory matrices, older pair/pthread,
selected origin/reuse/entropy and M4. New witnesses cover large/small actual
budgets, whole-request rejection, protection faults, middle-span zero reuse,
stale handles and stop/replacement. Builds 180 seconds, VMs 30 seconds and owned
teardown 3 seconds; force-kill fails. Larger live-worker/full-engine admission,
SDK/reader adoption, cross-core invalidation, hardware/DMA, general VM and R1
assembly remain unqualified. Released pins and sibling repositories stay unchanged.

196 target cases qualify this snapshot: 190 fresh guests and six completed guests
recovered only after rebuilding byte-identical ELF, supervisor and kernel inputs.
This includes 162 maintained memory/thread cases, 14 origin/reuse/entropy, seven
M4, ten larger-owner cases, one unsupported envelope and two thread-view cases.
Full host/pin/workflow checks, 13 memory model tests, four partition/geometry tests,
17 launch tests and two actual removed-bound controls pass. Thread storage uses a
bare stack/FS cookie, not a production musl TCB. The thread-only supervisor checks
exact additional handshake yields through retained output; the ordinary 64-yield
oracle stays unchanged. Large images are denied on small peers before generation
mutation; five failed requests do not consume lifetime admissions.

The first three-large-image-generation test timed out under the unchanged
30-second watchdog. Its separate BSS/admission witness now repeats BSS and stale
checks in all three generations and the full allocation exercise in generation
1; the ordinary positive retains two full-budget generations. Every failed
attempt is retained. Allocation/range scans are quadratic at this private quota;
bounded operation latency is the next local prerequisite before larger worker or
public engine admission. Passing correctness checks do not establish latency.
Current unmap clears user PTEs and restores kernel alias write permission under
IF-clear, flushes CR3, then zeros/reuses storage before returning to user execution.
It does not separately flush before restoring that kernel-only write permission.
