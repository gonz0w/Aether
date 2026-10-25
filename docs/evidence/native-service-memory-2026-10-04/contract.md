# One larger native service memory owner (before code)

Requirement: exercise a service budget beyond the existing 8 MiB profile without
inflating every domain's payload or metadata. Add a private BSP AENSUP01-only
`native-service-memory` profile requiring existing external backing and large
image/backing prerequisites. Domain 0 receives 8192 pages (32 MiB); the other
three domains retain 128 pages each. The same retained 64 MiB physical pool owns
all partitions; its tail remains ungranted. This is a trial memory budget, not
measured full-engine admission: recorded image/worker-stack lower bounds motivate
trying 32 MiB, but allocator/ARC pressure and native peaks remain unqualified.

Use one statically allocated 8192-record metadata array and three 128-record arrays
outside the stack. Only this profile borrows bounded page/payload slices. Ordinary
State arrays/layout and existing external fixed-length views remain unchanged.
Generation reset rebuilds both descriptors from authoritative domain identity and
clears that owner's metadata; descriptors are never caller nominated. Tables stay
at the existing 32 per domain: contiguous 32 MiB anonymous memory needs 16 leaf
spans, plus actual loader/stack spans; sparse exhaustion must remain atomic rather
than invent unbounded table storage. No dynamic allocation, new memory object/map
API, quota query, factory authority or global registry is introduced.

Pure reservation uses each actual borrowed metadata length for backing, arena and
record bounds. Keep the legacy typed 128/2048 interfaces and constant-size plans.
New sliced plans remain constant-size; no borrowed metadata may escape IF-clear
preflight/commit. Per-domain query and thread stack/TLS bounds use the actual quota.
Only supervised startup is allowed before RAM consumption; it may admit the larger
service at slot 0 and a small peer at slot 1. Supervisor slot 2 stays small. Existing
live/lifetime thread limits, masks, exact-ID retirement and context pins remain.

Test full available-budget mapping across more than four leaf spans, quota failure
with unchanged query, RO/NONE/unmap hardware outcomes, middle-span zero reuse,
failed preflight, image/stack bounds and exact supervised stale-handle/replacement
cleanup. Check a small peer cannot acquire the large budget. Actual omitted zero
and protect controls must fail the named witness; release builds reject existing
negative controls. Unsupported C/other envelopes and missing profile prerequisites
reject before pool use. No kernel payload pointer subtraction or cross-owner byte
reuse; detach/flush precedes write restoration and zeroing as already qualified.

Run new pure view/partition cases, full host/pins/workflow, both complete embedded/
external memory matrices, older pair/pthread compatibility, selected private origin/
reuse/entropy and seven M4. The unchanged isolated alias builder's prior source
binding remains historical coverage, not a fresh run count. Preserve every attempt,
actual source/tool/command/artifact/time receipts and every archive readback before
owned duplicate cleanup. Missing independent reader/consumer/SDK reviews remain
coverage gaps; no sibling/pin modification or engine/filesystem/release claim.

Simplicity/security: keeping every domain at 8 MiB cannot test the observed larger
service demand. Increasing four embedded payload arrays wastes memory and hides
one-owner geometry. Three small metadata pools plus one larger array and trusted
bounded slices directly express current ownership, avoiding an allocator or
general VM layer. Keep one table builder and existing capability/lifecycle paths.
The new unsafe boundary is reconstructing aligned payload and metadata views after
State reset; prove their partition bounds and owner lifetime in host and native
replacement checks. Larger live-worker admission follows only after this memory
path passes; do not change thread counts in this experiment.

Pre-retry finding: a large image fits the service but may not fit a small peer.
Factory admission must preflight its loader backing (including fixed main stack)
against the selected owner's records before generation/State mutation. Return
ENOMEM without spending generation or panicking. Test a real >128-page ELF with
small-peer admission denied repeatedly, larger admission/replacement passing and
small-owner metadata remaining intact. The existing parser's 2048-page large
image ceiling remains; the 8192 budget is for image plus runtime allocations.
First stop test's guest passed, but a wrapper expected a serial stop marker that
this profile never emits. Preserve it, qualify the actual compiled supervisor's
(144,3) terminal check and run fresh after the admission guard change.

Attempt 2's three-large-image-generation guest completes generations 1 and 2,
then times out after admitting generation 3. The ordinary positive already passes
two full-budget service generations and the small peer under the 30-second bound.
For the separate image-budget/BSS witness, repeat large BSS initialization and
stale/failed admission checks in generations 2/3 without duplicating the longest
allocation scan. Keep its generation-1 full-budget exercise, all ordinary positive
allocation checks and the existing watchdog. This is a narrower distinct oracle,
not a passing timeout or a performance/latency claim. Retain every timed-out byte.
Linear allocator/range indexing and bounded kernel operation latency remain a
concrete trigger before widening this private quota into a public engine profile.

Attempt 2's three-large-image-generation guest completes generations 1 and 2,
then times out after admitting generation 3. The ordinary positive already passes
two full-budget service generations and the small peer under the 30-second bound.
For the separate image-budget/BSS witness, repeat large BSS initialization and
stale/failed admission checks in generations 2/3 without duplicating the longest
allocation scan. Keep its generation-1 full-budget exercise, all ordinary positive
allocation checks and the existing watchdog. This is a narrower distinct oracle,
not a passing timeout or a performance/latency claim. Retain every timed-out byte.
Linear allocator/range indexing and bounded kernel operation latency remain a
concrete trigger before widening this private quota into a public engine profile.

Attempt 3 passes the first six guests, then the metadata-retry fixture fails 212:
it expected ENOMEM while the existing denial control returns EACCES. Correct only
that fixture expectation. Retry rebuilds final ELF, supervisor and kernel for the
six completed cases, requires exact byte identity and identical runtime inputs,
and preserves their actual old envelope/ISO/QEMU/serial receipts. Only the remaining
four cases run fresh. Record recovery explicitly; no changed implementation, failed
guest or stale artifact may be reclassified as a pass.

New thread-view witness: enable only the existing two-slot thread grant on the
same large/small profile, after full-budget release. A bare aligned stack and FS
cookie use the unchanged 96-byte storage descriptor. Both domains must reject
stack/TLS beyond their own query endpoint (including the small owner's endpoint
within the larger arena), pin live storage, reject running retirement, then clear
TID/observe/exactly retire/unmap and restore quota. Release/acquire atomic flags
hold the worker while pin checks run; no stack-local argument outlives confirmed
stop. Actual omitted thread pin control must fail the exact fixture check. This
is not a production musl TCB or larger live-worker admission.

Thread attempt 1 cannot find stdatomic.h under the strict no-host include path.
Retry adds only the pinned Clang 21 resource directory as an explicit last include
path and binds every resource-header digest. SDK headers remain first; no host
include discovery or hand-written volatile handshake replaces C atomics. Verify
no undefined imports/relocations or libatomic dependency in the actual static ELF.
Retain the failed source/command/diagnostic before this private compiler-path change.

Thread attempt 2 reaches exact retirement then fails fixture 237: existing native
observe returns ENOENT (-2) when no child slots remain; EBADF (-9) distinguishes
missing IDs while some child exists. Correct the last-child expectation, preserving
runtime and thread limits. The pure removed-view guard also fails correctly, but its
wrapper expected TestExpectedError rather than Zig's TestUnexpectedError for a
wrong error kind. Preserve both; match the exact Invalid/Exhausted assertion on retry.

Thread attempt 3 completes both workers with status 0, then its supervisor rejects
additional primary yields from the readiness/exit handshake. Keep the ordinary
64-yield oracle unchanged. A separate thread-only supervisor reads a four-byte
little-endian counter through the existing retained-output seam, checks exact
output length and bounded <=2,000,000 handshake yields, then requires the native
primary count to equal 64 plus that counter. The helper counts each actual primary
yield; child yields remain separate. Partial writes retain offsets. No public
output format, kernel counting, raw authority or accepted failure is changed.
