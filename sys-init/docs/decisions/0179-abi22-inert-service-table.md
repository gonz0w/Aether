# ABI22 inert service table and startup-test separation

2026-10-03; BG-067; experimental local policy, not a shared descriptor ABI.

Requirement: make the current three-role launch policy inspectable and validate
it at build time, while removing the startup wait/grant test probe from an explicit
new composition. Preserve the existing ABI22 developer baseline and exact grants,
paired ownership, protocol assertions, epoch bounds and fail-closed cleanup.

Use one constant Rust data table in startup order: Backend (image/slot1), Runner
(image/slot0), Command (image/slot2). Store role, image slot, order and automatic
retry count. Validate exact membership, matching role/image/order and zero retry
at constant evaluation. This profile has one supported topology; changing role,
image or ordering requires a matching protocol implementation and new evidence.
A table does not confer authority: the existing kernel entry and launch boundary
still enforce grants and slots. Epoch reuse is not failure retry. Zero retries
rejects an unimplemented promise rather than silently ignoring configured policy.

The simpler alternative is documenting scattered constants alone. That does not
bind owner selection and native image mapping to one checked definition. Choose
constant data rather than adding a JSON parser/generator, dependency graph or
package descriptor at this stage. This removes duplicated role/slot policy in the
new profile and the test delay from its startup path. It borrows the conventional
static service-table idea and existing paired owner, requiring no new subsystem.
The retained baseline continues its original test probe; broader protocol test
coverage and supervision remain separate. No obsolete historical driver is removed.

Acceptance: compile-time rejection of swapped/missing/duplicate role-image-order
and nonzero retries; exact old baseline image compatibility; fresh table-profile
useful command/cleanup/halt and halt before admission without the idle probe;
scoped new linked-stack inspection and 16 KiB image bound; full local checks.
Sources, tools, logs and failed attempts are retained in a new packet. Do not infer
boot performance, full product configuration, dynamic service support, automatic
recovery or assembled release from this slice. POSIX portability remains at the
policy/explicit boundary; native execution is Aether x86_64 only.

Foundations O-01–05, I-01–06 and E-01–08 apply. Distribution SV candidates remain
unimplemented; RL scope/evidence and existing ABI22 transport separation apply.
Experience boot markers remain unchanged. Released pins and sibling files stay
unchanged. This is local technical review, not independent release sign-off.
