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
