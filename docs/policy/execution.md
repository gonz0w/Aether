# Aether execution policy

Canonical sections extracted from [PROJECT](../../PROJECT.md). Local policy is
bound to the containing source revision; external pins retain their own identities.
Existing owner change authority and all applicable contracts remain in force.
Commands and literal repository paths below keep their original working directory;
only Markdown links were rebased for this file.

## Current milestone execution direction —2026-11-01

Cam approved the [fixed reader profile](https://github.com/gonz0w/Aether/issues/97#issuecomment-6563209702)
and [standing direction](https://github.com/gonz0w/Aether/issues/97#issuecomment-6563276253):
“yes these type of requests are auto approved, i only want work to stop for desing
decisions or hard blockers.” For the selected filesystem/TTY/Zsh milestone,
routine bounded implementation and fit corrections and separately reviewed QEMU
checks may proceed within existing resource, disposable-media and no-network
boundaries without another per-step confirmation. This explicitly supersedes the
older per-run confirmation clauses below for that routine scope only.

Keep finite scope, affected checks, separate review, exact source/artifact/media
binding, one attempt per reviewed proposal and known stop/cleanup. Stop a cohort
at its first unexpected result. Diagnose and correct the failure, then review a
fresh matching candidate before another bounded attempt; consumed attempts stay
consumed. The standing owner instruction supplies execution authority for that
reviewed routine candidate. A local record or agent review cannot create it.
Stop for consequential design, authority or product decisions or genuine hard
blockers. No hardware, release/deployment, ambient authority or unbounded resource
expansion follows from this direction.

The approved default-off `native-mktemp-reader` profile enlarges physical
`State.output` to320 bytes in the existing private BSP read-only ABI14 closure.
Only engine slot0 has logical320-byte capacity; other slots and default profiles
retain256. Four States add256 raw bytes; actual linked aligned kernel static growth
must be measured and must not exceed16KiB. Larger growth needs an owner decision.
Per-request256/per-transfer16 limits, pointer and authority checks, eight-byte
observation format, query bounds and generation reset remain unchanged. No new
syscall, capability kind or ABI is introduced. Reuse the frozen reader engine,
controller and envelope artifacts; only the reader kernels/ISOs need rebuilding.

## Selected terminal MODE and transmitter-empty query —2026-11-01

Cam directly approved the reviewed [issue121 design](https://github.com/gonz0w/Aether/issues/121#issuecomment-6566036292):
“Approve this scoped design (Recommended)”. This selects explicit MODE permission
for the one admitted test application's terminal relationship and one opt-in,
console-holder-only nonblocking int81 operation `0x26004`. Existing limits and
default profiles remain unchanged. The accepted proposal identity is
`fe5446691ac214ee4331d7770ae9cae7a97f5064c02d2068b0ac088dd45d7c12`;
separate peer review is
`e79003da2596f794d3d3f44b85a2ca433a79272eb1fe12dfb7c2c4c30f2b9f6d`.
The published lifetime and GET-revision clarifications in that issue bind this
selection. Do not request the same design approval again.

The query accepts only F001 from the existing exact live console holder under
current slot/generation/admission/closed checks, with all auxiliary arguments
zero. It observes COM1 LSR once, enabling receive-error retention before reading
status. Return zero only for valid TEMT, EAGAIN while busy, and EIO for all-ones
or impossible TEMT-without-THRE. Preserve receive bytes and pending receive errors. The selected profile enables
retention before every initial LSR poll, including earlier write-status polls.
No raw port selection, pointers, queue, allocation or kernel wait is added.
Existing read/write, `0x26002` close and `0x26003` handoff keep their contracts.

Rust retains waiting and mode policy under the original absolute deadline and
attempt/containment bounds. The selected experiment saves mode, applies real
ICRNL with TCSADRAIN, verifies its byte effect, restores and verifies raw CR on
the existing duplex descriptor. Public mode controls require the original live
MODE-bearing reference, exact caller/generation, control token and applicable
revision. The unpublished private duplicate in the existing fourth alias slot
is only for trusted local cleanup after confirmed app stop; it cannot authorize
public requests after the original reference retires. GET has a zero request
body and returns current revision; SET/RESTORE compare expected revision.

This authorizes the scoped implementation and its focused checks. The standing
milestone direction covers separately reviewed finite QEMU candidates and normal
GitHub delivery. No quota, alias capacity, raw PIO grant, service placement,
canonical/ISIG/group support, native EINTR, full Zsh or R1 acceptance follows.

## Ordinary-app namespace and clock contract —2026-10-28

The owner approved the separately reviewed [issue98 proposal02](https://github.com/gonz0w/Aether/issues/98#issuecomment-6477628920)
for implementation and bounded host/offline-fit work. Proposal identity is
`258723ec94c221185e379fe7e67becd55b1497fd6efcbcdb36d565945e8a080e`;
separate technical review is
`7b19aa147eb9603131a993a7886ca5fd582022cefa4a5dfa1533b89e4bd73095`.
The decision covers one positive ordinary-app temporary-directory experiment.

Implement the fixed launch record of 320 bytes and startup record of 64 bytes, atomic
pre-greeting handoff of the sole AF09 namespace connection, and a distinct
read-only monotonic-clock grant bound to the app's nonreused lifetime. The
reviewed kernel operations are 0x2300a and 0x28012, startup tag 0xa003 and clock
capability kind 0x36. Preserve existing operations and callers. The proposal's
holder, direction, generation, epoch, admission, revocation and copy/exec denials
remain part of the accepted contract.

Use the existing 304-byte descriptor startup and stream wire for stdout/stderr,
with the reviewed one-app sys-init stream owner and app-local musl vector-write
adaptation. The app's actual EOF/EPIPE observations and once-only raw closes do
not establish engine export: sys-init independently requires app/engine terminal
outcomes, ordered export, reclaim and existing clean-halt settlement.

Ordinary limits remain 1 MiB ELF, 128 image-plus-fixed-stack pages, 128 backing pages
and 4096 TLS bytes, with 64 KiB mapped stack and initial SP at 48 KiB. Existing engine,
owner, channel, capture, source-freeze, retention and focused-test limits remain.
No larger Zsh profile, resource exception, ambient authority, SDK/provider rebuild,
new filesystem wire operation or general broker is selected. Implementation
requires finite issues, affected checks and separate review before integration.
This decision grants no QEMU, hardware, native sufficiency or release acceptance;
a later campaign needs its own reviewed artifacts and explicit execution grant.

## Bounded Zsh application trial —2026-10-25

The owner approved implementing and host-testing the separately reviewed
[application profile](https://github.com/gonz0w/Aether/issues/69): a distinct
1.5 MiB application ELF cap, 384 image-plus-existing-stack pages and 640 total
backing pages in each of five fork-capable application slots. The engine retains 8192 pages and
the owner retains 128. This assigns 45 MiB within the existing 64 MiB backing
reservation; 19 MiB remains ungranted. The selected application image window is
`0x200000..0x400000`. Existing capability, TLS, stack/bootstrap and ownership
checks remain binding; older profiles retain their defaults, selectors and seals.

At the admitted image limit, at least 256 backing pages remain for all later
runtime allocations, including TLS and allocator overhead. This is a bounded
trial resource decision, not evidence of Zsh heap/stack sufficiency. Routine
implementation and host verification follow the finite issue scope, required
checks and separate review. No guest, native prompt or ISO qualification is
authorized by this decision. Exact SDK/artifact qualification evidence stays local.
## AF09 diagnostic control review —2026-10-26

The owner reviewed and approved the concrete [issue75 diagnostic](https://github.com/gonz0w/Aether/issues/75)
from draft PR76/head `88a83fab808221cec5770b3db447d849478688ee`.
Introduce the compile-time `native-af09-drain` selector with default `none` and
exactly `file_prefix`, `exec_prefix`, `fork_prefix`, `stream`, `no_ack`,
`partial_ack`, `exit_deadline` and `pending_fragment`. Omitted/explicit `none`
retain ordinary behavior. This satisfies DEVELOPMENT's human-review requirement
for this closed non-boolean control; do not ask for the same review again.

Implementation, host verification and matched offline artifact preparation may
proceed under the [diagnostic contract](../../docs/NATIVE-AF09-DRAIN.md). Existing
profile/authority/resource limits, source freezes, cleanup, separate review and
major-handoff checks remain. This adds no runtime selector, guest permission,
resource exception, native sufficiency or release acceptance. A later guest
requires its concrete reviewed artifact and execution disposition.
## AF09 offline family budget —2026-10-26

The owner adopted a standing5400-second aggregate for the complete
[issue75](https://github.com/gonz0w/Aether/issues/75) offline admission/drain
family: file_prefix, exec_prefix, fork_prefix, stream, no_ack, partial_ack,
exit_deadline and pending_fragment, with twenty prepared roles in total.
One clock covers the whole selected suite from preflight through final input
verification, publication and owned cleanup; case and builder calls do not renew it.
Other target suites retain their1800-second ceilings.

Children remain180 seconds, live stdout/stderr4MiB each and compiler files16MiB.
Focused host300/complete host900 limits, source freezes, all tests, existing media
allowances, runtime authority/memory/request bounds and known cleanup stay binding.
This time-only default grants no guest, native sufficiency or release acceptance.

Earlier failed campaigns remain failed. Triage failures, correct their cause,
recheck affected inputs and obtain separate preflight review before a justified
fresh complete-family attempt. Do not blindly retry unchanged failed work or
replay unknown mutations. This standing default does not require another approval
for each ordinary corrective attempt inside its scope; a larger bound or another
consequential resource change remains the owner's decision.
