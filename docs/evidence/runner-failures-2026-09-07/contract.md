# UL-059 operational delivery failures

2026-09-07, before implementation. Extend only the selected AEOUT001 fixture.
Kernel/build/pins, sibling repositories, old profiles and authority stay unchanged.
Aether owns transport/effect oracle; userland owns parsing and consumer adoption.

Qualify a zero or EIO write after exactly 16 accepted bytes, including stderr
usage diagnostic failure; actual 512-byte backend exhaustion from a 528-byte X
probe; and a consuming close returning EIO after complete help output. On any
failure, the client stops delivery, closes both aliases once and exits 1.
The owner independently records the exact failure, forbids writes after a delivery
failure, verifies the exact retained prefix and empty other sink, input bytes,
both alias closes, backend close/stale denial and two-generation reclamation.
Close EIO here is a confirmed consumed alias, not an ambiguous backend cleanup
result. Owner still verifies/cleans every backend handle after readback.

Negative clients retry a failed write, hide operational failure as success, ignore
close failure or fabricate exit1 without attempting output. Exact failure/prefix/
status/request-count oracles must reject each; no arbitrary exit1 acceptance.
No replay, successful truncation or invented unknown-state recovery. Ambiguous
channel/reply/close outcomes remain separately blocked coverage, not qualified by
this deterministic error witness. Capacity probe is not user-facing CLI text.

No new unsafe boundary, dependency, kernel quota or ABI. Use existing bounded
buffers and traps. Rustfmt1.98.0 edition2024 and Clang-format21 approved config;
retain legacy harness style with scoped additions. Full command suite plus prior
connections/inherited-launch, host/Zig/pin/workflow/format checks. Freeze sources,
retain all attempts, update reference/inventory/STATE and exact evidence.

Close reply rule for this carrier: a complete, otherwise valid EIO close reply
confirms consumption of that alias and permits cleanup of the other role. Legacy
profiles still poison on every nonzero close reply. Other malformed/unknown
close replies still poison AEOUT001. This narrow rule must be explicit in the
transport and reference; it does not infer backend cleanup from client close.
