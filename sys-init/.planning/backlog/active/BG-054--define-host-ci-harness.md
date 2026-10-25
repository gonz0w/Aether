# BG-054 — development harness and CI

Status: partial, Aether-only scope revised by the maintainer on 2026-10-22.

Keep useful host/model/parser tests, pinned tool checks, required-suite completeness,
watchdogs, owned cleanup, failure triage and compact evidence. The existing runner
and EHT-01 results apply only to their captured source/tool snapshots.

Other-OS product support, Linux/BSD/illumos qualification matrices and portability
shims are retired. They are neither deferred requirements nor unrun release blockers.
No replacement platform campaigns or native runtime adapters are needed for this
scope change. Hosted CI selection/scheduling and independent reviews remain
separate development/publication work; no provider execution is claimed.

For current checks use [DEVELOPMENT-CHECKS](../../../docs/DEVELOPMENT-CHECKS.md)
and root [DEVELOPMENT](../../../../docs/DEVELOPMENT.md). Native owner/process work
requires its own matched build and consuming witness; the current priority is in
root [STATE](../../../../.planning/STATE.md). Preserve all released pins and runtime
limits. The [prior chronology](../../../docs/archive/2026-10-22-bg054.md) is historical
reference only, including its superseded cross-host expansion requirements.
