# Bounded Dash script integration

BG-067, reviewed2026-09-09. The [verified intake and three local replays](evidence/dash-script-intake-2026-09-09/README.md)
provide a concrete next step in sys-init without waiting for interactive shell or
sustained-init completion. Do not replace the accepted ABI9 bytecount runtime pin:
this packet is an additional candidate configuration, not an interchangeable image.

## Compatibility and ownership

Review sources are in the hashed producer/sources.tar.gz and sources.json from
that intake. Relevant paths are user/native-command/cat-roles.rs, cat-bootstrap.h,
startup-adapter.h, transport.h, kernel/arch/x86_64/native_c.zig and build.zig.
Producer command-results.json records the exact build selections and images.

| Boundary | Existing sys-init | Script configuration and required change |
| --- | --- | --- |
| Roles | Runner0, stream backend1, child command2; Native maps its Role to image/slot. | Dash0, stream1, read-only file service2. Preserve paired owner but explicitly bind images/slots per service; slot2 is an EOF-driven provider, not the old command role. Both providers need Role::Backend semantics, without conflating their grants or channels. |
| Startup | AERUN001/AERIO001 runner and child admission. | Selected AECAT004224-byte carrier: stream descriptors, advisory metadata, scoped CWD query and separate read-only file root. Root authority comes from the delegated connection, not UID/GID or PWD. Do not accept it through the old carrier parser. |
| Protocol | Command launch/collection and stream file aliases. | Direct shell lifecycle plus two bounded service-backed file descriptions. Reuse the selected producer bridge and exact oracles first; do not import every cat-roles fixture mode or implement another filesystem. |
| Cleanup | Command/runner terminal, stream readback, client cleanup, backend EOF/terminal/reclaim. | No live file records, shell terminal/cleanup, then explicit EOF and terminal17 for each provider before endpoint/reclaim completion. Producer currently uses direct checked traps; replace lifecycle calls with our retained-owner operations. Preserve its original stream-then-file terminal ordering for the consuming witness. |
| Kernel selections | Old command profile accepts terminal kinds1–3. | Parent identity, public signal/action routing, memory and runner-local/files options are selected. Same basic envelope shape/slot count does not mean identical behavior. Freeze these exact selections and do not enable kind4 or claim signal termination without its own contract/witness. |
| Bounds |8 KiB code,4 KiB stack, three slots/six channels; bounded generations. | Existing pool limits remain. Measure the adapted supervisor through its enforcing linker and fresh target run; old bytecount size is not a shell size estimate. No larger profile is selected. |

## Smallest next implementation

Bind three paired owners explicitly to the selected roles/images. Start and validate
file and stream services before publishing Dash startup. Keep current borrowed
handles and confirmed/Unknown cleanup rules; a stop acknowledgment is not terminal
or file-record retirement. Use per-service adapter bindings so both providers can
send EOF without weakening the owner's Role::Backend check. Retain actual errors
and endpoint progress after partial allocation/launch.

First build a sys-init-owned positive script image and both current negatives from
these frozen inputs. Require exact hello-newline output, ordered0/17/17 terminals,
two generations/six reclaims, and unchanged1501/1599 zero-reclaim rejection.
Then qualify relevant partial launch/stop cleanup before broader acceptance.
Rebuilding the owner while reusing verified producer Dash/service ELFs must be
labelled as such; it is not a fresh upstream Dash/libc build. Extract any further
required target members only against the already recorded archive/member hashes.

## Limits and simplicity review

The producer explicitly leaves V4 malformed/truncated admission, independent
opens/exhaustion/stale/alias offsets and ambiguous backend replies incomplete.
Unexpected backend failures reject its fixture; they are not recoverable failures.
Do not broaden the initial consuming claim or silently enable automatic retry.
General paths, ENV, external commands/pipelines, interactive TTY, persistent
storage, independent userland acceptance and sustained operation remain separate.
The [sustained handoff](SUSTAINED-INIT-HANDOFF.md) still applies, but does not block
this bounded script integration. No sibling edit/request or shared pin update.

SE review: the requirement is real script execution under our small owner. The
simpler alternative is keeping the producer owner, which supplies replay evidence
but does not qualify sys-init ownership. Choose the existing constant-state paired
owner and the already demonstrated protocol; no new manager or filesystem is
needed. Remove direct success-only lifecycle assumptions only in the selected new
adapter, preserving old fixtures and error/authority checks. O-01/04, I-01/03–06
and E-01–08 govern this boundary. No new shared rule or exception is proposed.

## First sys-init-owned native script — 2026-09-09

[Three fresh native cases](evidence/dash-script-owner-2026-09-09/README.md) pass:
actual script execution and the original missing-root/missing-close rejections.
The fixed binding uses three persistent paired owners; both providers receive
explicit EOF and terminal observation before reclaim. Positive code is8176 bytes.
Earlier8320/8208-byte link failures remain retained, not booted. Five old command/
stop supervisor variants remain byte-identical after the shared launch extraction.

Maintained `prototypes/native-command/script_lifecycle.rs` binds each service;
`script-owner.patch` adapts only the hashed producer cat-roles.rs. Builds use local
frozen sources and original Dash/service ELFs. Other cat-roles modes are outside
this patch's selection. Local slot/role validation returns Known EINVAL without a
kernel call; these are distinct from captured kernel errno. No new unsafe site.

This completes the first script lifecycle slice. Next qualify partial launch and
stop cleanup with this composed file bridge; retained component tests do not
establish its interruption semantics. Producer failure-matrix/ENV/exec/pipes and
sustained operation remain separate. SE review is in the linked evidence; no
new framework, shared pin or sibling modification was required.

## Startup-prefix rollback qualified — 2026-09-09

[Five native probes](evidence/dash-script-launch-2026-09-09/README.md) verify actual
invalid-startup EINVAL at file/stream/shell launch, retained endpoint cleanup,
provider EOF/terminal/reclaim and two omission controls. Stream startup's three
empty file handles must be closed even when no shell starts; the initial failed
probe exposed that obligation and is retained. Three ordinary images remain
byte-identical. These are explicit rollback probes, not an automatic product boot
recovery path; their short-prefix result1605 is an expected profile rejection.

Next controlled stop after shell admission with live file references. Broader
allocation/unknown errors retain their separate evidence; no new profile/pin,
unsafe site or sibling change. The linked record contains the SE review.

## Stop with a live script reference — 2026-09-09

[Two fresh native cases](evidence/dash-script-stop-2026-09-09/README.md) pass at
8192/8032 bytes: stop after actual open but before the first backend read, and
omitted file closure. The owner requires143/kind3 and clean request EOF, closes
retained backend file handles with stale denial, retires stream aliases and then
runs existing readback/provider cleanup. Two generations/six reclaims pass; the
omission rejects1599/reclaimed0. Three normal images and five startup probes remain
byte-identical. No profile, pin, unsafe-boundary or sibling changes.

This is pre-dispatch cancellation only. The stop image has no code headroom.
Next consolidate normal startup failure handling using the qualified rollback
obligations; probes alone do not install automatic recovery in the normal boot
entry. Broader file-error recovery and sustained operation remain separate.

## Normal startup integration capacity — 2026-09-09

The candidate fails the unchanged 8,192-byte linker limit; diagnostic measurement
is9,152 bytes (960 over). It was not booted. Maintained adapter/patch bytes are
restored to the native stop checkpoint. See
[retained attempt](evidence/dash-script-startup-capacity-2026-09-09/README.md).
Automatic ordinary-startup rollback remains incomplete. Next resolve this specific
profile's capacity through scoped design review or a matching producer handoff,
then rerun native script/rejection/rollback/stop cases. This does not reopen the
historical ABI16 capacity decision or authorize a larger ABI9 mapping.

## Startup size review — 2026-09-09

Nine scoped layout measurements do not resolve the code limit: eight remain9,152
bytes; constant-slot specialization grows to10,528. No candidate was booted and
validated runtime sources are unchanged. Local producer handoff and exact acceptance
workload: `docs/DASH-STARTUP-CAPACITY-HANDOFF.md`. BG-067 now waits for a matching
capacity decision/packet; no sibling request was sent. Broader refactoring and
shelved features are not substitutes for this boundary.

## ABI17 consumption — 2026-09-11

Capacity is resolved for the bounded startup integration: ten native script cases
and four compatibility/admission cases pass. Normal rollback is9,152 bytes and
the largest selected stop image9,264 within the explicit16,384-byte profile, with
the unchanged4,096-byte stack. See `docs/evidence/dash-startup-abi17-2026-09-11/README.md`.
The opt-in script-abi17.patch requires bootstrap17; old ABI9 inputs remain available.
Actual launch EINVAL rollback is qualified; additional startup-error coverage and
sustained wait/reuse/shutdown remain separate. Released pins and siblings unchanged.

## Startup error coverage — 2026-09-11

Six native denied-grant allocation cases cover both channel positions at all
three startup slots; three injected Unknown responses exercise fail-closed startup.
Ten prior supervisor images rebuild identically. First-attempt errno expectation
was corrected from EPERM to the actual EACCES; its failure is retained. See
`docs/evidence/dash-startup-errors-2026-09-11/README.md`. Synthetic Unknown responses
are not kernel ambiguity witnesses. No production behavior or released pin changes.
Next product boundary: sustained wait/reuse/authorized shutdown and useful-session
integration; additional framework and broad failure campaigns remain outside scope.
