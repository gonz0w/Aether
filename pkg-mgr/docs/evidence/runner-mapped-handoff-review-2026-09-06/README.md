# Mapped runner handoff review — 2026-09-06

[Input review](review.json) verifies five immutable owner evidence manifests:
NB-03 (1,643 entries), NB-04 (1,809), startup (5,942), mapped results (3,660)
and mapped uncertainty (3,480). Counts are manifest entries across bundles, not
unique files or independent test cases. Copied summaries/receipts preserve bytes.

The latest 53-case combined run and nine legacy cases have matching retained
ISO/serial hashes, artifact maps and client build receipts. [Semantic log review](semantic-log-review.json)
checks ten mapped positives across two generations with six reclaims, plus six
uncertainty rejects. Normal statuses 0/1/2/64/125/126/127/134/255 are preserved;
fault kind2/detail134 maps to parent1. Uncertain admission/collection wrappers
101/102 and retry mutant109 reject at broker970/reclaimed0, without success.
Wrapper exits are test observations, not public CLI statuses or remote recovery.

NB-03/04 and opt-in parser/startup/mapped-result evidence supersede the older
pending notes. The receipt still names aether-userland.native-command-userland.v1
and explicitly excludes complete public CLI/CR-01 acceptance. All controls and
feature flags must remain explicit when building a package consumer. Do not alias
this receipt to fileio-libc, discard negative cases, execute receipt commands, or
relax identity checks. Existing package harness selectors remain unchanged.

Next bounded implementation is a separately named command-runner transport profile
against this exact receipt and producer closure. It needs package-stage image
reconstruction, exact 53-case oracles and negative identity/case-set tests before
acceptance. This inspection alone is not that consuming witness. Local help/error
outcomes need the owner's proposed extension; startup negatives, pending budgets,
ASan and independent reviews remain separate. No native shell/package admission,
filesystem durability, service activation or release approval is established.

No runtime or sibling source was changed and no native process was executed.
Standards/development/whitespace checks and documentation input hashes are retained
in validation.json. Frozen host archive and all existing pins are unchanged.
