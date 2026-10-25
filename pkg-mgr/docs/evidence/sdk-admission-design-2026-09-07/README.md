# Cross-SDK admission design checkpoint

2026-09-07. [Proposal](../../SDK-ADMISSION-PROPOSAL.md) records the proposed
profile grammar, caller policy, byte binding, explicit operation scope, legacy
compatibility and failure oracles. inputs.json binds reviewed sources and design
bytes. checks.json retains documentation-only standards/development/whitespace
checks. No parser, schema, supported command, recipe or native runtime was added.

The proposed independent profile pin prevents self-consistent bundle/profile
substitution from being accepted merely because all supplied hashes agree.
The profile also binds exact receipt bytes without asserting native behavior from
an architecture string. Actual owner receipt selection and review remain pending.
All listed runtime acceptance cases and SDK-01–08 remain NOT RUN. No full runtime
suite was rerun for this documentation-only change; previous runtime evidence is
not counted as proof of the proposed branches. Release pins, sibling repositories
and unrelated Origins implementation work are preserved.
