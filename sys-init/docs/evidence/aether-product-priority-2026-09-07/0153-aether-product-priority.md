# 0153 — Aether product first

Maintainer direction, 2026-09-07.

The maintainer prioritizes a working Aether init product. Defer additional OS
provisioning, cross-platform development/test qualification and hosted platform
expansion until that product milestone, then revisit with the maintainer. Preserve
POSIX-oriented design, explicit platform boundaries and portability rationale;
this changes execution order, not the goal of portability. Keep existing local
checks for changed code and require fresh Aether witnesses for native behavior.
Do not run more Linux/BSD/illumos campaigns merely to fill deferred coverage.
Retain current tools, pins, tests and historical evidence; deferred is not complete.
Independent release review remains required for its actual claims, but is not a
blanket blocker to authorized Aether implementation.

Next: BG-058 PH-06 native errno history retention and closed terminal
inspection/replay without reset, continuing decision 0094. Review the current
Aether contract and pinned producer inputs before choosing the bounded native
slice; do not infer new APIs from companion progress. BG-057 retirement and
BG-033 recovery remain follow-ons. No runtime behavior changes in this priority
update and no new native success is claimed.

Documentation impact: repository instructions, entry point, planning, quality
process, integration gates and coverage inventory reflect this order. Historical
evidence and earlier decisions are preserved. Run existing local full checks.

Validation: all ten existing local gates pass in `run-kfjoi8oy` with unchanged
sources during the run. Evidence: `../evidence/aether-product-priority-2026-09-07/`.
This is prioritization, not new runtime acceptance.
