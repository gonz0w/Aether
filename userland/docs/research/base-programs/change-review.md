# UL-064 provider-matrix review

Date: 2026-09-05. Scope: documentation and source research for contributors.
Requirement: turn UL-011's package shortlist into explicit command/provider,
prerequisite and acceptance planning. No implementation or package admission.

Applicable rules: Foundations E-01–08; Distribution PX-01–04 and trust gates;
approved documentation DW/DS/DP, coding CD-01/04 and testing TD-01/TC-01/TE-03.
Inputs and retrieval limitations are recorded in review.json. Dash archive identity
was verified against the existing source lock before reading its builtin table.
Web sources are dated research leads; no upstream build inputs were executed.

Success: cover the original required commands, distinguish builtins/executables,
identify pending Toybox applets, preserve provider uncertainty, connect actual
pkg-mgr script needs and record build/native/security follow-ons.
Forbidden outcomes: claiming a native utility from a web listing, treating a digest
as source authentication, inheriting grants from an applet name, or modifying sibling
package/ABI contracts. No owned-resource lifecycle or executable behavior changes.

Validation: offline quality gate (host Python, 220-second outer deadline), local
file-link existence checks for added/changed research references, required-command
coverage review and stable BP ID uniqueness. No runtime tests are relevant to these
documentation changes. All runtime, upstream-suite and security-audit work remains
explicitly unexecuted. Tests and original evidence are unchanged.

Documentation: BASE-PROGRAMS.md is the canonical provider matrix; PACKAGES.md routes
to it. Quality inventory remains draft. No manuals, diagrams or public CLI changed,
so renderer and command-runtime checks are not selected.

Technical review: assistant inspected upstream status/docs and pinned local dash
source; independent reviewer pending. Reader walkthrough not performed. This is
reference planning, not an onboarding or recovery procedure. No exception granted.

Follow-ons: UL-065 first provider build; UL-066 awk/tr/stty comparison; UL-011 stays
active. UL-063 remains prerequisite to UL-058 behavior work. Source trust remains
UL-016. No performance/security superiority or full POSIX claim is made.
