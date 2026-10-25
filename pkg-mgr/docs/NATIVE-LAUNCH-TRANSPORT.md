# Launch, channel and read-only file-service transport

The package-owned host transport consumes the existing kernel-owned dual-image
profiles without changing their ABIs or granting service activation. Each has an
explicit command, destination and receipt format:

| Command in `mk/aether-supervised.py` | Envelope | Destination | Receipt format |
| --- | --- | --- | --- |
| `stage-launch` | AENEX001 | aether-launch-v1 | aether-launch-transport-v1 |
| `stage-channel` | AENCH001 | aether-channel-v1 | aether-channel-transport-v1 |
| `stage-connections` | AENMX001 | aether-connections-v1 | aether-connections-transport-v1 |
| `stage-connections-small-pool` | AENMX001 | aether-connections-small-pool-v1 | aether-connections-small-pool-transport-v1 |
| `stage-coexist` | AENCO001 | aether-coexist-v1 | aether-coexist-transport-v1 |
| `stage-coexist-small-pool` | AENCO001 | aether-coexist-small-pool-v1 | aether-coexist-small-pool-transport-v1 |
| `stage-process` | AENFS001 | aether-process-v1 | aether-process-transport-v1 |
| `stage-files` | AENFS001 | aether-files-v1 | aether-files-transport-v1 |
| `stage-files-writable` | AENFS001 | aether-files-writable-v1 | aether-files-writable-transport-v1 |
| `stage-files-writable-memory` | AENFS001 | aether-files-writable-memory-v1 | aether-files-writable-memory-transport-v1 |

Commands take `ROOT BASE_RECEIPT_SHA256 NATIVE_BIN NATIVE_SHA256`, as in the
[supervised transport](SUPERVISED-HANDOFF.md). ROOT must be a private initialized
root with a verified five-artifact boot v2 bundle. Publication adds one envelope
to those five exact payloads; neither stage nor verify boots or launches it.

These profiles bind `required_kernel_options` to actual JSON booleans.
`native-memory` is false except in `files-writable-memory`, where it is true;
`smp` is false throughout, matching the accepted witnesses consumed here. The memory-enabled writable variant has separate explicit evidence below.
Existing supervised and [memory](NATIVE-MEMORY-TRANSPORT.md) receipt bytes and
commands remain compatible; a newer envelope is never silently reinterpreted.

## Validation boundary

The dual-image header is the owner-defined 56-byte prefix: magic, two ELF lengths,
supervisor length, reserved zero, and 32 developer entropy bytes. Exact total size,
both 64-byte-or-larger ELF64 little-endian x86-64 executable identities, per-image
1 MiB ceiling and 1–4096 supervisor bytes are checked. This is structural transport
validation, not full ELF admission: mapping/layout rules remain kernel-owned.

Receipts bind the complete six-payload inventory and base receipt pin. Wrong
magic/profile, options (including integers masquerading as booleans), lengths,
reserved field, either ELF identity, pending package replacement and repeated
publication are rejected. Existing payload-pin/inventory/symlink guards remain.
The sixteen-fixture development gate exercises all twelve transport profiles.

A declaration of kernel options cannot prove compiled configuration. The opt-in
witness harness obtains payloads from accepted, externally pinned ISO images,
checks their exact envelope identity, stages them, rebuilds an image and runs the
owning profile's native oracle. Package hashes establish identity, not signer
trust, release clearance or source-to-binary reproducibility.

## Completed witnesses

[Retained results](evidence/native-launch-channel-2026-09-05/README.md) cover:

- Kernel launch: positive selection/cleanup; wrong-image and layout semantic
  rejection; malformed-machine and reserved-field rejection before publication.
- Kernel channel: ordered transfer and cleanup after normal exit, writer fault
  and controlled stop; wrong-count semantic rejection.
- Userland UL-038 channel: all six independent consumer cases, including
  11-byte writes / 7-byte reads, original startup arguments after private-source
  mutation, EOF/EPIPE, wrong-count and corrupted-final-byte rejection.
- Userland UL-039 read-only file service: independent fragmented request/reply
  client, positive access, corrupted data, truncated frame and weakened-root
  semantic rejection.
- Kernel read-only file service: positive script/text access and handle cleanup,
  corrupted-data and truncated-request semantic rejection.

Negative boots require the specific terminal/supervisor details and exact panic,
never a generic timeout or unrelated boot failure. Positive boots require the
profile's exact success marker and three reclaims. The read-only file service
embeds its two files in the test service; it is not writable or persistent storage.
The UL-038 supervisor is the kernel conformance client, not sys-init adoption.

## Reproduction and evidence integrity

`tests/native-launch-integration.py --help` lists required arguments. Supply:

- `--profile launch|channel|process|coexist|connections|files|files-writable|files-writable-memory` and `--producer-kind kernel|userland-channel|userland-files|userland-fds|userland-failures|userland-libc|userland-stdio|userland-broker|userland-coexist|userland-connections|userland-shared|userland-inherited|userland-inherited-libc|userland-fileio-libc`;
- the accepted `--evidence` JSON and external `--evidence-sha256`;
- a separately pinned `--tools-evidence` and `--tools-evidence-sha256`;
- the matching local `--aether` source/tool directory and a new `--root`.

The two evidence pins can identify different accepted runs: the earlier launch
witness predates a smoke-message change, so its exact payloads are tested with
separately pinned newer smoke tools. This is explicit, not an assertion that all
producer sources match the older run. No evidence command is executed: only
known build arguments are read to locate the pinned ISO within selected outputs.
The tools are copied into a private tree and checked against their source pins;
local boot dependencies are copied and verified. Config/license bytes must match
the accepted ISO. No download, kernel rebuild or sibling mutation occurs.

Before/after checks cover producer evidence, accepted ISO bytes, the frozen tool
closure and package implementation inputs. Every subprocess has a timeout and
an isolated process group, cleaned up by the harness. Inputs, commands, logs,
receipts, rebuilt images and incomplete runs remain under the supplied private root.
An invalid producer pin fails before creating that root. The package-side reader
accepts only the explicitly supported evidence schemas/case sets it explicitly handles; it is not
a general runner for arbitrary evidence documents.

## Next dependency

UL-040 writable scratch is now consumed alongside its fresh read-only regression.
UL-041's descriptor consumer is now supported by the witness harness over the
existing writable transport. UL-042 failure handling and UL-043 bounded libc calls now have explicit consumer
selectors as described below; transport does not supply recovery. Sys-init has not adopted
the launch/channel producer, and its general event/deadline/recovery model remains
separate. The shared PD-01–PD-12 draft still awaits affected-owner review.

Useful native shell/package execution additionally requires adopted file/path and
executable lookup, writable storage where required, process/exec/wait and descriptor
semantics. Reference dash success, bounded launch and an embedded read-only script
are not native dash or native pkg-mgr execution. Transport work can proceed with
concrete owner artifacts; it cannot supply or silently select those missing contracts.

Owners: [launch](../../docs/NATIVE-LAUNCH.md),
[channel](../../docs/NATIVE-CHANNEL.md),
[files](../../docs/NATIVE-FILES.md),
[userland consumer](../../userland/experiments/native-channel/README.md),
[shared proposal](../../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).


## Explicit writable scratch profile (UL-040)

`stage-files-writable` uses the existing AENFS001 envelope and required kernel
options, with a separate destination/format and mandatory
`service_mode: "volatile-scratch-v1"`. Missing, unknown or relabelled mode metadata
is rejected. The mode describes the service build, not a new kernel option or a
capability grant. Existing read-only receipt bytes stay unchanged.

The envelope itself has no writable-mode discriminator. Structural verification
cannot infer service semantics from its magic or stop a caller from repackaging
arbitrary pinned code under a different declaration. This remains unauthenticated
research transport. The consuming witness binds the accepted ISO and userland
report, requires an actual boolean writable selection plus the recorded service
`--cfg writable`, and boots the exact transported bytes with independent assertions.
Mode metadata alone is never admission or execution authority.

[UL-040 transport evidence](evidence/native-writable-transport-2026-09-05/README.md)
contains four writable boot outcomes and four fresh read-only regression outcomes.
Writable positives check creation, capacity, immutable seeds, read-only views,
stale handles, gap zeroing and truncate/extend clearing. Wrong data, skipped
zeroing and ignored rights require client exits 205, 219 and 218 respectively,
supervisor 611 and the exact rejection panic. Read-only controls retain their
separate statuses; positives require result 100 and three reclaims.

One service-local scratch file is limited to 64 bytes and disappears on service
exit. Lost mutation replies remain unknown outcomes; no automatic replay, fsync,
persistent installation, native shell redirection or sys-init activation follows.
The package-owned change neither modifies sibling implementations nor republishes
shared standards. See the [userland contract](../../userland/experiments/native-files/WRITABLE.md).


## Bounded descriptor consumer (UL-041)

`--producer-kind userland-fds --profile files-writable` selects the independently
accepted descriptor case set. No new envelope, package format or service mode is
introduced: the userland descriptor table is a client of the same volatile scratch
service. The harness requires boolean `descriptors: true`, writable service mode,
the recorded client `-DDESCRIPTORS`/`-DWRITABLE` selection and the existing service
cfg check. Ordinary file consumers require descriptor mode false or absent.
These declarations are checked against the exact pinned accepted images and boots;
they are not a new signer or source-to-binary verification guarantee.

[Descriptor transport evidence](evidence/native-fd-transport-2026-09-05/README.md)
records four descriptor outcomes and eight fresh read-only/writable regressions.
The positive checks shared positions for aliases, independent-open positions,
capacity/failure behavior, dup2 replacement and handle lifetime. Frozen offsets,
early service close and leaked final close must yield client 207, 213 and 216,
respectively, plus supervisor 611 and the exact profile panic. Success requires
supervisor 100 and three reclaims.

This is a private negative-errno API, limited to four local descriptors and two
open-file records. It does not interpose libc, establish fork/exec inheritance,
standard descriptors or native shell acceptance. Closed-transport rejection does
not establish recovery after an unobserved mutation. UL-042 owns direct reply-loss,
malformed-reply and final-close fault evidence; broader process/TTY, persistence,
service ownership and release trust remain separate. The [owner contract](../../userland/experiments/native-files/DESCRIPTORS.md)
defines the exact userland scope.


## Failure-handling and libc consumers (UL-042 / UL-043)

The existing `files-writable` transport also accepts two explicit witness modes:
`--producer-kind userland-failures` and `--producer-kind userland-libc`.
No runtime transport, receipt format or kernel ABI changes are needed.

The harness checks exact boolean descriptor/failure/libc selections and the
recorded compiler defines before accepting a complete case set. Failure cases
require their particular injection/mutation defines; the libc client requires
LIBC_FILES, WRITABLE and its POSIX feature declaration. Cross-mode evidence is
rejected. Producer commands remain data; the harness never executes them.

[Recorded package witnesses](evidence/native-libc-transport-2026-09-05/README.md)
cover the latest UL-043 bundle: seven failure cases, four libc cases and twelve
descriptor/read-only/writable regressions, totaling 23 rebuilt-image boot checks.
Four failure-handling successes deliberately discard/change complete real replies
and require normal final cleanup. Ignored poisoning, leaked temporary references
and relaxed reply checking require client 195, 193 and 189. Libc wrong errno,
ignored flags and frozen positions require client 200, 201 and 205. Each negative
requires supervisor 611 and the exact profile panic; it cannot pass on timeout.

The failure wrapper injects faults at the consumer boundary after real service
replies. This is not physical channel loss, service restart or a recovery protocol.
The test-only raw RPC checks are independent effect inspection and cleanup, not
production recovery or permission to replay an uncertain mutation.

The libc witness uses musl read/write/close/dup/dup2 and adapted public open/lseek.
It covers bounded short I/O, errno, shared offsets and unsupported-operation
rejection. It does not establish internal stdio paths, threaded cancellation,
creation policy, inherited descriptors, native shell execution or persistent
installation. UL-044's buffered-file audit is the next userland boundary; process,
exec, TTY, lifecycle integration and release trust remain separate.


## Buffered FILE consumer (UL-044)

`--producer-kind userland-stdio --profile files-writable-memory` consumes the
bounded FILE witness. Dynamic FILE allocation requires the existing owner native
memory option: the distinct transport receipt records `native-memory: true`,
`smp: false` and `service_mode: "volatile-scratch-v1"`. Its AENFS001 envelope ABI
is unchanged. Existing memory-disabled writable receipts retain their exact format
and semantics; the new profile does not silently widen them.

The harness requires exact stdio/libc/descriptor mode booleans, client STDIO_FILES,
LIBC_FILES and WRITABLE defines, the feature declaration, writable service build,
and explicit native-memory=true in every accepted image build. Missing/conflicting
memory options or using the old writable profile rejects before output creation.
As elsewhere, declarations identify required configuration; pinned image bytes
and native boot oracles establish the scoped runtime witness, not authenticity.

[UL-044 evidence](evidence/native-stdio-transport-2026-09-05/README.md) records four
stdio boots and 23 fresh regressions. Positives require normal final cleanup.
Original input fflush, vector corruption and leaked polling errno require client
189, 186 and 196 respectively, supervisor 611 and the exact profile panic.
The underlying musl archive stays unchanged: userland supplies pinned candidate
replacement objects and internal vector/seek adapters. Their source/build identity
is retained in the producer report, not inferred from package transport hashes.

The witness covers buffered bytes/EOF/seek, input-flush failure preservation and
retry, ENOSPC/ferror, failed implicit flush with descriptor closure, FILE-list
cleanup and real dynamic allocation. Valid local buffers and single-thread use
remain limits. This is not public vector-I/O, all FILE modes, formatted I/O,
automatic exit flushing, native process/exec/TTY or persistent installation.
UL-045's native dash gap review and owner-mechanism handoff is the next userland
step. [Owner contract](../../userland/experiments/native-files/STDIO.md).


## Connection-bound launch broker consumer (UL-046)

`stage-process` selects the existing AENFS001 ABI-5 broker witness with a separate
`aether-process-transport-v1` receipt and destination. Required native-memory/smp
options are both false. This is not a file service or writable scratch declaration:
the Rust broker occupies the conformance supervisor domain, launches one requester
and services fixed launch/collect frames over its exclusively delegated channel
pair. The connection's immutable namespace contains only the worker executable.
The two image payloads are requester and worker; inheritance is explicitly empty.

`--profile process --producer-kind userland-broker` requires the exact six-case
independent consumer schema and accepted image pins within the selected captured
producer output. It uses receipt-matched captured tools, never the moving sibling
checkout. [Evidence](evidence/native-broker-transport-2026-09-05/README.md) retains
the pinned report, source restorations, all six staged/booted outcomes and controls.
Structural envelope verification cannot infer broker/file policy or authenticate a
caller-relabelled bundle: the distinct format expresses intent, while pinned
accepted images and independent boot oracles establish this particular witness.

Positive execution requires worker slot 1 generations 1/2 exiting 17/33, requester
slot 0 exiting 29, result 100/reclaimed 3 and the existing file-service pass marker.
Allow-inheritance, wide-scope and repeat-collect must reject at requester 51/52/66.
Partial request and requester exit require 41/42. Every negative requires broker
903 and reclaim count 1 for partial-request, 2 for the others, followed by the exact
profile panic. No timeout or generic failure satisfies these oracles.

Empty inheritance, connection tickets and name selection are not POSIX fork/exec,
inherited open-file state or recovery after a lost reply. This two-channel broker
cannot concurrently host the file-service pair under this accepted profile.
UL-047's newer coexistence witness remains separate. Sys-init's SI-04 sequential
cross-slot reuse fault is also separate; this run cannot claim it fixed or widen
replacement ordering. No sibling source, shared ABI or standards pin changed.
[Owner contract](../../docs/NATIVE-PROCESS.md) and
[independent consumer](../../userland/experiments/native-process/RUNTIME.md).


## Independent broker/file coexistence (UL-047)

`stage-coexist` consumes AENCO001 / ABI 7 with native-memory=false, smp=false and
native-coexist-small-pool=false. `stage-coexist-small-pool` is the explicit negative
control transport, setting only that pool option true with its own destination and
receipt format. Both use the same bounded 56-byte/two-ELF envelope layout. Existing
AENFS001 and other profiles cannot silently reinterpret the new magic.

`--profile coexist --producer-kind userland-coexist` accepts the six independently
accepted consumer cases, checks exact per-case pool build selection, and chooses
the reduced-pool transport only for `small-pool`. Metadata describes required
configuration; exact pinned images and the runtime oracle establish the scoped
witness. The reduced-pool control is not accepted normal configuration.

[UL-047 evidence](evidence/native-coexist-transport-2026-09-05/README.md) contains
six coexistence boots plus six fresh ABI-5 broker regressions. The positive requires
backend slot 1 generations 1/2 both exiting 17, requester 29, result 100/reclaimed 3
and `AETHER NATIVE COEXIST PASS`. Repeat collect, partial request, requester exit,
small pool and wrong data require requester 66/41/42/59/78 respectively. Negatives
require broker 903, one reclaim for partial request/small pool or two otherwise,
and exact profile panic with no success marker.

The requester sends raw file frames through the broker while both channel pairs
are live. It exercises seed bytes, scratch, denied-create side effects, full-body
frame consumption, foreign/stale tickets and backend reset. This does not establish
the local FD/stdio facade through that broker, inherited open-file references,
fork/exec, pipes, native shell, persistence or sys-init adoption. ABI-6 shutdown
and SI-04 replacement order remain independently scoped. Newer ABI-8/9 capacity
artifacts await their own consuming witness; UL-049 owns the next userland review.
[Independent contract](../../userland/experiments/native-process/COEXIST.md)
and [kernel contract](../../docs/NATIVE-COEXIST.md).


## Two-client connections consumer (UL-049)

`stage-connections` explicitly consumes AENMX001 / ABI 9. The 80-byte header has
magic, three ELF lengths, supervisor length, two reserved-zero words and 48 entropy
bytes. Each ELF is bounded to 64 bytes–1 MiB; ABI-9 supervisor code is 1–8192 bytes.
The earlier package reader imposed an unnecessarily narrow 4096-byte limit;
UL-051 corrects it to the existing owner bound, without changing the ABI.
Exact total size and all three ELF identities are checked before publication.
Older envelope readers do not accept it. ABI 8's separate program-stop workload
was reviewed by userland but was not independently executed or adopted here.

Native-memory and smp remain false. The existing native-coexist-small-pool option
is false normally and true only in the separate `connections-small-pool` control
receipt/destination. ABI 9 normally selects six channels; the control reduces it
to four. The receipt is required-option metadata, not proof of compiled policy or
capability authority; accepted pinned images and native oracles supply that witness.

`--profile connections --producer-kind userland-connections` consumes the exact
six-case independent evidence set. [Saved results](evidence/native-connections-transport-2026-09-05/README.md)
record four QEMU boots and two prepublication structural rejections. A nonzero
second reserved word and a wrong third ELF machine reject in package transport;
their original producer boot evidence remains separate. Ordinary fixtures cover
both reserved words, all ELF identities, lengths and option/relabel boundaries.

The positive requires two exact terminal rounds in order slot 2/client29,
slot 0/client29, slot 1/backend17, then supervisor 100/reclaimed 6 and
`AETHER NATIVE CONNECTIONS PASS`. Reduced pool, rejected partial framing and
corrupt data require supervisor 950/959/960 with zero reclaims and the exact
profile panic. Corrupt data additionally requires slot 2 client44. No timeout or
unrelated panic can satisfy an oracle.

The independent clients validate fragmented progress, full reply bytes, endpoint
direction and authority denials. They do not adopt the local FD/stdio facade,
inherited open-file state, POSIX parenting, native shell or sys-init policy.
UL-050 owns independent acceptance of the distinct shared-files bootstrap using
the same ABI; matching envelope/marker alone cannot establish that contract.
General inheritance-list admission/rollback and persistent installation remain
separate. [Consumer](../../userland/experiments/native-process/CONNECTIONS.md)
and [owner contract](../../docs/NATIVE-CONNECTIONS.md).


## Fixed-alias shared files (UL-050)

`--profile connections --producer-kind userland-shared` consumes the distinct
`aether-userland.native-shared.v1` evidence and exact six-case set. It reuses the
AENMX001/ABI-9 transport with the full pool; no new receipt, envelope or runtime
helper is needed. The earlier two-client connection schema is not sufficient to
accept these semantics, despite sharing a marker and native ABI.

[Six package boot witnesses](evidence/native-shared-transport-2026-09-05/README.md)
cover fixed bootstrap aliases with descriptor indices 3/10, rights 3/1 and shared
position. Both clients independently validate bootstrap/reply fields, reference
scope, malformed close preservation and exact `ab`/`cd`/`ef` read progression.
Child-first and parent-first repeat for two fresh generations, with exact terminal
orders 2/0/1 and 0/2/1, clients 29, backend 17 and six reclaims. Frozen offset and
early close require parent slot 0 status 50; missing rights guard requires child
slot 2 status 48, all with supervisor 970/reclaimed 0. Missing final close requires
owner supervisor 975/reclaimed 0. Every control requires the exact profile panic.

The final-close stale backend-handle probe is owner code; the independent clients
prove their tested alias behavior and surviving access. The rights mutation
observes ENOTSUP in place of required EACCES, not an unauthorized successful write.
Only explicit EAGAIN responses are retried in the bounded client protocol; lost or
malformed mutation replies are not replayed. This is fixed bootstrap delegation,
not parent-requested spawn, dynamic inheritance admission, libc/FD interposition,
POSIX parenting, native shell or persistent installation.

UL-051's parent-requested inherited-launch witness is the next independent
consumer boundary. Same ABI/marker alone cannot close it. Shared standards and
owner policy remain unchanged. [Userland contract](../../userland/experiments/native-process/SHARED.md).


## Parent-requested alias admission and result collection (UL-051)

`--profile connections --producer-kind userland-inherited` consumes the distinct
`aether-userland.native-inherited.v1` nine-case report. The transport still uses
AENMX001, native-memory=false, smp=false and the full channel pool. Its three-image
supervisor ceiling now matches the owner's existing 8192-byte ABI-9 bound; the
previous 4096-byte package restriction rejected the valid 5288-byte broker. Tests
accept 4097/8192 and reject 8193; older single/two-image limits are unchanged.
Receipt fields and older successful bundle bytes remain compatible.

[Nine package boot witnesses](evidence/native-inherited-transport-2026-09-05/README.md)
cover child-first, parent-first, rejected native launch and partial channel
reservation with successful bounded retry, plus five semantic mutations. Every
successful case repeats two terminal rounds with clients29/backend17 and six
reclaims. Parent-first orders 0/2/1; the others order 2/0/1. Leaked reservation,
leaked admission, accepted excessive rights, altered child status and repeated
successful collection require parent70/70/66/75/76 respectively, supervisor970
with zero reclaims and exact profile panic.

Independent parent/child code checks one-entry admission, narrowed connection-bound
alias rights, explicit rejected-admission rollback, shared reads, generation-scoped
receipt validation and consuming observed result collection. File-alias closure and
child-result ownership remain separate. The owner supplies actual native admission/
reservation mechanisms and the final backend-close probe. Incorrect rights admission
acceptance does not establish a successful unauthorized child write.

Retries apply only to explicit injected EINVAL/EBUSY admission responses and bounded
EAGAIN collection polls; lost or malformed replies abort, without transparent replay.
This is not general descriptor-list admission, libc integration, fork/exec/waitpid,
POSIX parenting, shell or persistent storage. UL-052's libc/FD-to-broker review and
bounded workload definition is next. No sibling source, shared release or native
ABI was changed. [Consumer contract](../../userland/experiments/native-process/INHERITED.md).


## Musl read/close on inherited references (UL-053)

`--profile connections --producer-kind userland-inherited-libc` selects the final
`aether-userland.native-inherited-libc.v1` fourteen-case witness. It uses unchanged
ABI-9 transport and receipt bytes. Raw inherited-client acceptance does not prove
this new libc path; the schema, case set, accepted image pins and independent
oracles remain explicit. [Evidence](evidence/native-inherited-libc-transport-2026-09-05/README.md)
retains the final source run with connection-wide poison checks and frame counters.

Four successful admission/lifecycle scenarios retain exact two-round terminal
order and six reclaims. Five inherited broker mutations retain parent70/70/66/75/76.
Wrong invalid-FD errno and forced errno contamination require parent80/82. Dropped
read, corrupted read and dropped close require parent122 after the fault probe
has checked EIO, no byte publication for reads, local close consumption and no
subsequent file/admission/collection frames. All ten controls intentionally reject
the workload at supervisor970/reclaimed0 with the exact panic and no success marker.
They do not claim successful remote recovery or six-reclaim cleanup.

The separate musl probe calls the new inherited binding without a local offset;
the broker owns positions and cross-client references. Exact ab/cd/ef reads, zero
and rejected-size no-transfer paths, errno and normal file-close/result independence
are checked. The candidate adapter supports exactly two-byte reads or local zero,
not general-size reads or application EOF; old local-offset/stdio profiles remain
separate. Valid local buffers, single-thread operation and explicit unsupported
calls are retained constraints. No sibling/shared transport or runtime receipt
changed. [Owner contract](../../userland/experiments/native-process/INHERITED-LIBC.md).

UL-054's general-size shared-read/EOF owner handoff is next. The proposed useful
command still needs concrete stdin/stdout/bootstrap and independent accepted output;
this bounded adapter does not establish bytecount, native shell or installation.


## General-size bounded shared I/O (UL-054/055)

UL-054 identified the completed owner file-io extension. UL-055 independently
consumes it through musl read/write/close; package selection is
`--profile connections --producer-kind userland-fileio-libc`, requiring its distinct
`aether-userland.native-fileio-libc.v1` final ten-case report. Existing AENMX001
transport and receipts are unchanged; two-byte inherited-libc evidence cannot be
substituted. [Saved package witnesses](evidence/native-fileio-libc-transport-2026-09-05/README.md).

One call makes one bounded transfer up to 16 bytes, returning short results for
larger buffers without prefetch/replay. The positive checks ab/cde/f across clients,
repeated EOF, unchanged bytes beyond returned data, zero operations, narrowed
rights, shared position, capacity rejection and append to a 64-byte record.
The broker independently reads back every byte (abcdef plus 58 Xs) before the
owner final-close probe. Two rounds require clients29/backend17 in order 2/0/1
and supervisor100/reclaimed6.

Frozen position, consuming zero-read and absent child-write denial require client
slot2/91, slot0/90 and slot2/93 respectively. Acknowledged but omitted writes require
owner supervisor985/reclaimed0. Wrong errno, contamination and three completed-reply
fault probes require parent80/82/122/122/122 and supervisor970/reclaimed0. Every
negative requires exact profile panic, not timeout or unrelated error. Dropped close
is injected after the required storage workload; its earlier mistimed producer
attempt is not accepted. Fault probes establish connection-wide poison/no replay,
not successful remote cleanup. Zero-write rights mutation is not a data overwrite.

This is one inherited binding and one volatile record, not open/seek/stdio, general
FD tables, two-record stdin/stdout or a real command runner. No sibling source,
shared adapter, receipt or standard pin changed. UL-056 reviews the proposed
CR-01 bytecount workload and concrete startup/stdin/stdout handoff next; useful
command, shell, lifecycle composition and release acceptance remain separate.
[Consumer contract](../../userland/experiments/native-process/FILEIO-LIBC.md).
