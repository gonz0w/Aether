# 0222 — Matched16-slot FILE/startup and public dup2

2026-10-23. Experimental implementation review and bounded native witness; no release.
Maintainer directs continued integration within current budgets. The domain
operation/version/error/authority/concurrency/test contract and SE-01–05 review
are canonical in [FS-FILE-REPLACE](../../../userland/docs/proposals/FS-FILE-REPLACE.md),
“Matching consumer and public dup2 implementation contract”. This decision routes
sys-init consumption rather than defining a competing shared standard.

New FILE AEFP0002 requires fs_dup2_wire/path/process/replace/file16 selection;
new startup/map/fork/exec versions reject old peers before effects. fd_startup,
fork gate, FILE peer and owner route compare their compile-time selections.
Opaque process generation, source references/rights, exact FILE masks, serialized
copy/admission, child-ready/exec publication, terminal/export/cleanup and uncertainty
retirement remain intact. Low FILE selectors never become console authority.
Existing56 owner tests exercise the actual selected geometry; all16 reordered
FILE aliases survive capture/inheritance. Default3–15 and old wires remain separate.
No new kernel API, mutable global, resource owner, unsafe boundary or field.

From system root:

`python3 -B sys-init/scripts/check-broker-init.py --libraries PRODUCER --compact-compare --unified-route --compose-owner --guarded-stack --exec-provider PROVIDER --paths --dup2`

Use the producer/provider commands in [compact evidence](../../../userland/docs/evidence/filesystem-dup2-owner-2026-10-23/README.md).
The complete selected owner fits41360 code/7528 resident/7992 conservative stack
within49152/8192/8184 usable; no writable image statics or allocator. Old path owner
reproduces40640/7504/8000. Source hashes, failed attempts and actual C/Rust fork/exec
correspondence/negative controls remain explicit. This is host/target build scope.
Root focused cadence supersedes older blanket full-suite recipes; no full native
or independent review claim. Current Python only; minimum runner missing.

A source-matched guardedv9 and exact three-guest diagnostic are prepared with
fixed self/CLOEXEC/FILE replacement/local10/stdin/shared EOF helper checks.
All current guest limits, file/media/guard/cleanup oracles and no-retry rule stay.
The approved three-guest sequence now passes actual helper7/parent0/engine0,
public dup2/stdin/shared EOF,21 cleanup rows,327 paired waits and halt1936/6000.
Both readers verify the full original file, recovery media/canaries are unchanged
and all VMs stop. Generated outputs removed after compact readback; no retry or
extra guest. [Native results](../../../userland/docs/evidence/filesystem-dup2-owner-2026-10-23/native-results.json).
This one-sequence approval is consumed. Changed qualified-source execution still
requires fresh scoped disposition under [the existing persistence rule](../../../docs/OPENZFS-FEASIBILITY.md#required-independent-disposition);
prior root-read approval is consumed. The requested persistent Zsh ISO remains
in progress; no RAM-only image or private dash helper substitutes for it.
Root STATE is authoritative for progress/next action.
