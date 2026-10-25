# 0102 — Offline standards-wrapper manuals

Accepted local documentation work, 2026-09-06; BG-056 follow-up to decision 0101.
Add canonical manuals for the Foundations, Experience and Distribution wrappers.
Describe actual ignored arguments, output/error behavior, local files, reference
scope and verification order. Do not imply the older Experience wrapper enforces
the stricter Foundations/Distribution lock and inventory rules. Document that
Experience/Distribution reference assertions depend on the inherited Python
optimization environment; Foundations uses explicit rejection paths.

Validate normal and ignored-argument invocations, plus isolated missing-lock
controls using unchanged wrapper copies with no release present. Record sources,
all lock/vendor identities, manual lint/78/60-column/HTML renders and required
aggregate checks. Preserve all release bytes, pins, protocols and siblings.
The manuals are documentation, not implementation conformance or publication.

Ten of eighteen developer commands now have manuals. Local source review exposed
follow-up verification work: Experience lock/symlink/pre-execution inventory
validation and explicit assertion-mode handling for Experience/Distribution.
Track these under BG-056 before claiming a uniform verification boundary. No
retained release may be rewritten to fix them; any wrapper change needs focused
negative controls and compatibility review. Independent/target review is pending.

Evidence: docs/evidence/standards-manuals-2026-09-06/README.md. The exact explicit
experimental OS STYLE notices retain decision 0099's scoped disposition.
