# UL-007 scratch intake review

Scope: read-only producer packet integrity and unchanged consumer oracle review;
no harness, runtime, sibling, pin or acceptance changes. Foundations E-01/04/05/08
and approved Testing TE-01/03 apply. Producer owns admission and file grants;
userland owns unchanged-script acceptance. Names confer no native authority.

Plan: verify all members of the three dated dash scratch boundary packets, retain
manifests and READMEs, verify all twelve consumer script/reference/stdout pins and
helper identity. Require the declared sole QEMU-prefix transformation exactly.
Run the local quality gate. These are host integrity checks, not native tests.
Use Python standard library; no subprocesses in intake, extraction or build outputs.
Reject absolute/traversing paths, symlinks and mismatches. Preserve failures.

Independent expected oracles come from the existing workload manifest and helper,
not producer results. Actual technical review: Codex source/oracle inspection;
independent owner/reader review pending. Full native handoff is still required.
No runtime evidence is reused to upgrade acceptance. Recheck current producer
state and pin the final replay kit before future execution. Existing six qualified
scripts remain unchanged. UL-007/M3, UL-081 and broader review gates remain open.
