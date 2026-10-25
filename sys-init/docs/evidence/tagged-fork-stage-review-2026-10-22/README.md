# Tagged fork staging source review — 2026-10-22

[Research and proposed requirements](../../research/TAGGED-FORK-STAGING.md),
[decision0201](../../decisions/0201-tagged-fork-stage-review.md). audit.json records
18 complete source deliveries/570 member hashes, unchanged linked v2 580-member
manifest and seven before/after-pinned source excerpts. Kernel excerpt includes
actual freeze/copy branches; full original file digest plus exact excerpt bounds
and digest are retained. No code/compiler/native run or independent replay of the
producer's link result. Source inspection is not a target behavior witness.

The new libc contract reports one missing __aether_fork_stage import. Current
source supports the narrower conclusion that old staging cannot carry the tagged
map, and that kernel successful copy clears source.frozen before current broker
API's required post-copy parent-frozen clone. This is a coordination/proof gap;
no kernel bug or required new primitive is inferred. No precondition is relaxed.
Child-only context/TLS/auxv rebind, known/unknown copy and cleanup semantics and
native complete dispatcher/fit remain open. BG-069/070 and OQ-025 retain follow-ons.

Copies are inert research evidence. Historical source/packet bytes are unchanged;
no sibling edit/message, external approval, new ABI/profile/quota/default/release
pin or native guest. Full offline checks are recorded in local-checks.json;
sha256.json seals packet except itself after validation. Existing runtime tests
remain scoped earlier witnesses, not rerun native acceptance for this source audit.
