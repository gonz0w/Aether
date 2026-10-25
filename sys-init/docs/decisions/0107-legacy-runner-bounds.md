# 0107 — Legacy native runner command bounds

Accepted host harness fix, 2026-09-06; BG-056 subprocess follow-up.
Use the existing bounded tool helper for lifecycle and supervision commands.
Add an optional working directory and a CompletedProcess-style adapter that
returns actual nonzero tool exits for the caller's semantic oracle. Timeout,
overflow and infrastructure failure still raise; they must not masquerade as
an expected guest rejection. Existing builder callers keep their defaults.

Keep native source, flags, variants and semantic markers unchanged. Preserve
120-second Zig/smoke bounds and add a 180-second lifecycle client outer bound;
all captured calls have a 4 MiB accepted-log limit. Attempt receipts retain cwd,
command, caller/helper identity, bounds and failure classification. Native
supervision adds helper/runner hashes to its producer source record. Existing
commands.json/results.json formats remain; adjacent receipts are additive.
Lifecycle compiler output is now merged into a retained client log and replayed
on stdout after success; compiler-error detail remains in that log rather than
being streamed directly. Failed Zig/smoke log prefixes now survive exceptions.

Run host cwd/nonzero/timeout/overflow/missing-tool controls and fresh three-case
lifecycle/five-case supervision witnesses from verified retained sources.
Native artifacts and successful semantic results must match the retained
profiles. Preserve failed attempts, including host sandbox restrictions.
No shared pin, sibling or native implementation changes are authorized.

Cleanup is limited to the owned process group of non-detaching children.
Nested builders create their own compiler groups with independent bounds;
an outer interruption does not establish complete nested-group cleanup. This
pre-existing composition limit remains explicit follow-up work, not a containment
claim. Copy/hash work is outside command deadlines. Record/API documentation,
remaining runner log limits and independent review remain open.
Evidence: docs/evidence/legacy-runner-bounds-2026-09-06/README.md.

Validation: six focused host tests, eight fresh native cases and all ten gates
pass (out/checks/run-rzmxebis). Eight envelopes match retained profiles; all
24 checked native source inputs remain unchanged. The initial socket denial
and successful new-workspace retry are retained. Updated manuals lint cleanly
and fit 78/60 columns. Independent review remains pending.
