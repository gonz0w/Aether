# Serial SESSION lifecycle producer — 2026-10-03

Before-code requirement: implement explicit AENMX009 / owner ABI24 selection with
`native-session-lifecycle`, reusing SI-07 owner clock/event/park/final-action
mechanics. Retain SESSION encodings, five worker slots, ten channels, fifteen
lifetimes, nine pipe epochs, three-child/two-pipe bounds, 24KiB owner and4088-byte
stack. Preserve all prior profiles and released standards pins.

Forbidden outcomes: accepting a mismatched selector or ABI, granting lifecycle,
UART or factory authority to a worker, fabricated progress on idle timeout,
wrapping identities, halting with retained resources, or claiming private probe
coverage as actual sys-init/shell/SDK acceptance. No sibling changes.

The simpler alternative is extending ABI23 or setting the ABI22 sustained flag.
Both would alter existing contracts: ABI22 changes identities and quotas; ABI23
has bounded observation finish semantics. One explicit profile and a shared
lifecycle predicate preserve these boundaries without duplicating the event core.
No obsolete consumer path is removed before matched consumer qualification.

Security/ownership: the actual supervisor slot and contextual grants govern every
operation. Interrupt-disabled comparison/registration and existing scheduler
publication serialize local events; there is no new shared mutable authority,
unsafe kernel boundary, dependency or user pointer operation. The Rust probe uses
the existing synchronous trap convention; its argument/read buffers stay live
through the trap, and writes borrow immutable bytes. Only kernel-owned UART status
and channel/terminal publications wake the owner. Wake means rescan, not success.

Selected checks: extended envelope framing/bounds host tests; full host/pin/workflow
checks; native positive long idle/channel/terminal/UART/reuse/clean halt and
semantic rejection controls; previous ABI22 mechanism and ABI23 selection controls;
M4 scheduler regressions. Missing full SESSION consumer suite/independent review
must be reported as a gap before adoption. Freeze runtime sources during native
runs; preserve failures and exact commands/artifacts. New output is private ASCII
probe markers, covered by the existing diagnostic exception; product output and
old machine markers remain unchanged.

## Results and scope

Final009 witness passes at3016 ticks/3007 idle with six genuine worker terminals
and six confirmed reclaims. SESSION task handles retain0xb0000001|(generation<<8),
not ABI22 typed IDs. Channel publication between snapshot/registration and worker
termination wake the owner. Stale task/channel references deny; malformed grants/
reserved fields and future sequence deny without event mutation. Input readiness
is level sensitive before consumption; after consuming one real byte, deadline
returns -110 without fabricating a new event sequence. Open UART and retained
channel ownership block halt; unsupported action and old fixture finish return
-38; closed/settled resources permit actual authorized halt.

Eight final new-profile native outcomes pass: positive, deliberately wrong worker
expectation, owner ABI mismatch, missing selector, wrong envelope with selector,
reserved envelope, truncation and over-limit owner. The wrong worker actually exits
77, is reclaimed/stale-denied, then the owner fails for that exact reason. Two build
controls reject mixed ABI22 selection and missing exec closure. Six reused worker
generations exercise the original scalar authority probe (its ABI22 label does not
claim userland ABI24 consumption). Native task/channel exhaustion and every halt
resource branch are not separately qualified by this new witness; existing pure
core bounds tests do not replace that future consumer matrix.

`zig build test` passes132 Python checks plus configured Rust/Zig and released-pin
checks;009 framing extends the host bounds/reserved/length matrix. Old ABI22 native
mechanism, all11 ABI23 prompt-driven serial cases using exact sealed payloads and
seven M4 target cases pass with current kernels. The older SESSION regressions
reuse sealed payloads rather than claiming fresh rebuilding of their SDK closure.
Source manifests/export archives freeze kernel/user/build inputs.
For another run, use the copy-to-fresh-packet command in NATIVE-CONNECTIONS;
the historical driver intentionally refuses to overwrite an existing label. All final native
manifests match current sources; the first positive is explicitly superseded by
`positive-final` after the host unknown-magic test and no-fabricated-sequence probe
assertion changed. No unrelated runtime edits occurred during qualification.

Linked owner raw/ELF equality and inspection pass:3064/24576 code bytes, estimated
stack352/4088, one immutable RIP-relative cell targeting linked memset and no
register indirect calls/jumps. This is a bounded contributor inspection aid, not
formal all-path or kernel stack assurance. Initial guarded-edit, obsolete host
unknown-magic rejection, over-strict inspection assertion and sandbox-blocked QMP
attempt remain retained. QMP regression was rerun with permitted local sockets;
all seven outcomes pass. No runtime change was made to evade the sandbox.

All experiment-owned artifacts are archived and every member read back before
removing their unpacked duplicate roots; see artifacts.json/cleanup.json. Sources,
commands, positive/negative traces, host and regression logs remain available.
BSD-2-Clause applies to original work; old dash/libc payloads retain upstream terms
in the referenced immutable serial packet. No sibling or release-pin changes.

## Next gate

The existing ABI23 fixture loops and actual sys-init composition are subsequent
work, not completed here. Adapt009 owner observation/drain/park and explicit policy
halt, preserving008 fixture behavior, then qualify the matching actual sys-init/
userland closure in the reviewed single supervisor domain. Full SESSION consumer
matrix, finite-exhaustion/resource checks, independent technical/reader review,
SDK disposition, persistent filesystem/packages and assembled R1 remain open.
No public ABI adoption or consumer acceptance is asserted by this packet.
