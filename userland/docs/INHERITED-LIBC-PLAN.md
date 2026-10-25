# Bounded inherited-reference libc integration (UL-052)

The next local experiment can proceed without a new kernel operation. Use the
UL-051 pinned admission/collection broker with a new userland read/close adapter.
This review selects an experiment, not a production POSIX service or shared PD
approval. No runtime code or compatibility status changes in UL-052.

## Why the existing file facade cannot be reused unchanged

`native-files/fd-layer.h` stores two open records containing backend handle,
position and local reference count, with four descriptor slots. Its protocol sends
an explicit offset and advances that local position after a successful read.
The inherited broker instead owns one position and the cross-client references;
clients receive connection-bound aliases at indices 3 and 10 and cannot send a
file offset. Copying either the old record or its offset into the new client would
create conflicting authority/state. Simply enlarging the four-entry array does
not resolve this difference. The older tested facade remains a separate profile.

The strict-musl SDK already routes read/write/close/dup/dup2 through `__aether_io`.
`native-channel/channel.c` also defines that symbol. UL-043 solved this boundary
by compiling its client channel object with the original hook renamed and providing
one facade hook. Reuse that build technique in the new experiment, leaving the
shared channel source and other profiles unchanged. Transport must call native
channel operations directly, never libc read/write recursively.

`libc-adapter.h` saves/restores errno around transport polling. Preserve that rule:
the hook returns raw negative errno and the existing musl wrappers translate it.
The hook must not leak an internal EAGAIN into a successful libc call. Keep a
separate probe translation unit so calls exercise linked musl symbols, with link
maps/disassembly showing the hook and excluding the threaded cancellation path.
The pinned musl close converts EINTR to success; this fixture must not produce
EINTR or claim interrupted-close semantics. Threads remain outside scope.

## Exact initial adapter scope (UL-053)

One local binding per client contains its validated reference, descriptor index,
rights and lifecycle state. It has no local file position, backend handle or
cross-client reference count. Publish it only after the complete bootstrap validates.
Indices 3 and 10 are explicit fixture bindings, not an adopted general table bound.
The separate launch/collection helpers keep their existing connection identity;
closing the file binding must not close their transport or discard their receipt.

| Entry point | Initial behavior |
| --- | --- |
| read on the live binding, count 2 | One broker read request; validate result/metadata/padding before copying at most two bytes |
| read, count 0 | Validate binding then return 0 locally with no RPC or offset change; no pointer dereference |
| read, other positive count | ENOTSUP before transport; never round up to two, consume hidden bytes or prefetch |
| read, count above SSIZE_MAX | EINVAL; null buffer with supported nonzero count gives EFAULT |
| write | Valid child binding: EACCES; valid parent binding: ENOTSUP; preserve raw owner denial probes in the workload |
| close | Remove local binding once; issue one consuming alias close; successful reply leaves separate collection usable |
| dup/dup2 | Valid source: ENOTSUP, including same-number dup2 in this explicitly limited profile; no unaccounted alias |
| invalid, negative or closed descriptor | EBADF before a file operation; avoid unsigned truncation |
| open/openat/lseek/fcntl, pipes and stdio | Not adopted; do not route older local-offset/public-open or FILE adapters into this profile |

This deliberately adapted read subset cannot serve general C applications. The
zero-length path implements a bounded no-transfer operation on a validated binding;
it does not simulate missing seek, duplication, launch or collection behavior.
Public unsupported operations must retain their real failure behavior if probed;
there is no blanket successful syscall fallback.

A completed broker EAGAIN is a known no-read result. Return it through libc and
let the bounded test workload retry explicitly. Do not turn arbitrary transport
backpressure, timeout or a lost reply into a safe retry. Native frame transfer may
poll EAGAIN while completing one request; it must never resend a completed frame.

On malformed/uncertain file replies, poison the local connection and return EIO;
subsequent use must not send another request. A read whose reply is lost may have
advanced the authoritative position. Do not repair that with a local offset or
replay. A consuming close whose reply is lost leaves the local binding closed and
the remote result unknown; repeated close returns EBADF. Preserve the failure
receipt and end the bounded workload. There is no reconciliation or successful
cleanup claim for that failure. Keep ordinary successful close/result collection
separate from this poisoned-connection policy.

## Concrete native workload and acceptance

1. Build fresh parent and child clients against UL-051's exact producer archive and
   tested strict-musl SDK. Keep admission/collection protocol calls explicit; do not
   rename them fork/exec/waitpid. Validate startup and direct authority probes.
2. Use actual musl read for `ab`, `cd`, `ef`, and musl close for the parent's alias.
   Exercise invalid descriptors, zero-length read, unsupported sizes, null buffer,
   duplication refusal and errno preservation before valid reads; exact later bytes
   must show that rejected/no-transfer calls did not consume the shared position.
3. Retain both exit orders, native-launch and partial-reservation rollback/retry,
   and one-time child status after normal file close. Preserve exact client/backend
   terminal order, six reclaims and owner final-backend-close probe.
4. Retain all five UL-051 broker controls (leaked reservation/admission, widened
   rights acceptance, wrong status and duplicate status) against the libc clients.
5. Add focused adapter controls: wrong invalid-FD errno; internal polling errno
   contamination; lost/corrupt successful read or close response. The last control
   records that the real operation completed before reply suppression, requires EIO,
   verifies poison/no replay and no local resurrection, and expects explicit failed
   workload cleanup rather than a success marker.

A new native pass is required before changing the compatibility inventory. Retain
sources, command/tool pins, maps, ELF inspection, exact envelope/ISO/serial hashes,
expected terminal contexts and unsuccessful attempts separately. Freeze inputs
before runtime; reject input drift. Existing protocols/markers/standards stay fixed.
No source or native-code change was made by this review, so no native suite was
rerun. All three local standards checkers pass.

## Required extensions before broader use

| Need | Responsible boundary / missing witness |
| --- | --- |
| Arbitrary read sizes, zero-length/error ordering and usable EOF | Owner file protocol must expose bounded general reads without deterministic two-byte scheduling; independent libc cases then consume it |
| Seek and multiple opens | Owner operation for authoritative position changes and multiple records; no client-only seek |
| Duplication / descriptor replacement | Local mapping plus explicit owner reference-lifetime contract; source retention, replacement close failure and descriptor bounds need tests |
| Flags / CLOEXEC / inheritance lists | Reviewed atomic admission/filtering and flag semantics; a fixed child index 10 is not F_DUPFD_CLOEXEC support |
| write and FILE buffering | Explicit writable operations/error semantics plus internal libc vector/seek/flush review; no silent read-ahead across shared positions |
| Standard streams, executable selection, argv/env | Owned bootstrap and namespace contract beyond the fixed fixture images |
| Shell process/pipe/TTY semantics | UP-02 and relevant owners: fork/vfork/exec choice, normal/failed executable replacement, pipes, signals and job control |
| Lost admission/collection/close replies | Defined unknown-outcome reconciliation, lifetime and shutdown contract; retries alone are insufficient |

These are local findings routed to existing UP-01/UP-02, not new canonical shared
requirements or sibling implementation edits. Future shared requirements belong
in Aether-standards through affected-owner review. The PD record remains pending
with zero reviews at this checkpoint. Review input hashes and exact snapshots are
retained in [evidence](evidence/inherited-libc-review-2026-09-05/README.md).

## Subsequent execution

UL-053 completed [fourteen native cases](../experiments/native-process/INHERITED-LIBC.md)
on the selected read/close scope. The plan above remains the review checkpoint;
current runtime details and evidence are in that result. The uncertain-reply controls
now include a connection-wide guard and outgoing-frame counts. Broader operations
remain open; UL-054 next specifies general-size read/EOF requirements.
