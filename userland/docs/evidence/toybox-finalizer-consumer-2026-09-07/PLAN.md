# UL-067 independent normal-copy adoption

2026-09-07. Consume the latest captured Toybox producer sources in a private build
root. Retain the producer recipe and record a local execution adaptation: fixed
paths, clean environment, pinned tools and existing owned process runner. Rebuild
all baseline Toybox translation units from the retained source; do not rely on
archived applet objects. SDK remains receipt-pinned. Reuse hash-checked owner
payloads for this first consumer run; owner source rebuilding is a later gate.

Scope: actual unmodified cat_main on binary32, empty and native short I/O, real
startup/mask/TLS/allocator, callbacks and flush, three consuming closes and four
native reclaims. Negative controls: skip copy, callback, flush and diagnostic close.
Require exact statuses and supervisor diagnostics, never a generic panic. No
filenames/options, public command registration, recursive/signal finalization,
error/usage acceptance or full CAT-01–08 acceptance follows from this slice.

Review Foundations O/I/E, C/CP/TD/TE and the existing quality process. Preserve
native roles/poison/rights, upstream notices, existing output bytes, SDK/archive
pins and smoke markers. No sibling implementation edits. Keep all attempts,
argv/environment/tool/source/artifact identities and raw logs. Builds <=180s,
guest watchdog30s; use the existing source-pinned native_smoke cleanup within an
owned process group. Run affected native cases and quality before reporting.
Review startup/finalization against docs/TOYBOX-NATIVE-CAT.md; document its remaining
close-error diagnostic and recursion boundaries. Independent reader review stays
pending. The release roadmap next step is native dash external command/pipeline.

## Error and usage continuation

Qualify captured errors (11 cases) and usage (20 cases) with the same source/SDK
closure and rebuilt Toybox objects. Add receipt-verified recipes and the owner's
recorded Rust build commands as separately pinned inputs. Errors rebuild the
selected supervisor with toybox_applet expectations; backend remains a verified
payload dependency. Usage reuses verified owner payloads. Resolve Rust directly
from the existing lock, avoiding ambient rustup selection. Preserve all original
case/status/prefix/poison and four-reclaim oracles. The whole-story producer rebuild,
finalization gaps and broad regressions remain separate. Keep each execution's
driver/recipe identity in a new directory so prior evidence is never overwritten.

## Captured finalizer continuation

The completed finalize delivery changes only the probe and opt-in owner branches.
Use a new snapshot, preserving earlier receipts. Select its18 buffered/flush/close/
status/re-entry/control cases and the7 normal-copy regressions. Rebuild all applet
objects and selected finalizer owners; backend remains pinned reuse. The repeat
hook guard is not a terminal re-entry policy. Final close-error diagnostics,
uncertain-close/diagnostic-failure coverage and full CAT-06 acceptance remain open.
Existing limits, original expected statuses, exact rejection contexts and four
reclaims apply. Retain technical review findings rather than weaken requirements.
