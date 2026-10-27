# Aether verification policy

Canonical sections extracted from [PROJECT](../../PROJECT.md). Local policy is
bound to the containing source revision; external pins retain their own identities.
Existing owner change authority and all applicable contracts remain in force.
Commands and literal repository paths below keep their original working directory;
only Markdown links were rebased for this file.

## Verification, instructions and maintenance

[DEVELOPMENT](../../docs/DEVELOPMENT.md#test-selection-and-cadence) owns the command/risk
map. Component commands run from their component directories unless stated otherwise.
The root Makefile retains aggregate entry points. `make check-system` is not an
assembled OS, boot-to-shell or release result. It and `zig build test` require
private standards and additional local inputs; they remain blocked when those
inputs are unavailable. See [PUBLIC-SOURCE](../../docs/PUBLIC-SOURCE.md). Sys-init's
`--current` gate leaves unavailable historical replay explicit. Missing tools, zero cases, infrastructure
failures and skipped checks are not passes.

Existing execution ceilings, stop-on-failure/no-retry rules, source freezes and
cleanup requirements remain scoped to their contracts. The complete host aggregate uses the scoped budget below;
onboarding's source-integrity/pure-Zig CI is no substitute. A failed or unavailable required gate stays
blocked coverage. No new guest disposition or expanded resource approval follows
from this policy or from hosted CI.
## Complete host gate budget —2026-10-26

Owner decision, 2026-10-26: the complete unfiltered root `zig build test` / `AT-HOST` gate
has a standing 900-second aggregate limit. Focused host aggregates remain 300
seconds; auxiliary/leaf limits remain 180 seconds and live diagnostic streams
remain capped at 4 MiB each. Existing sparse/artifact allowances stay unchanged.
All selected tests, exact inputs, source freezes, owned cleanup and compact
failure retention remain required. This changes only the complete host aggregate;
it grants no guest, runtime-resource, native, release or operational authority.

After a failure, retain and triage it, correct the cause, run affected checks and
review the resulting inputs before a justified full run under the existing test
cadence. Do not blindly repeat unchanged failed work, replay unknown mutations or
renew another scoped execution disposition. Historical one-run exceptions remain
consumed. A larger bound or another consequential resource change needs the owner.

Prose-only changes use applicable available source/link/syntax checks and separate
reader/source review. Standards-dependent checks remain required when selected
by the affected contract; unavailable inputs are blocked coverage, never a pass.
Prose-only changes do not imply an unrelated full suite, native guest or
source/build archive. Keep public summaries separate from local qualification
receipts; missing receipts cannot be represented as fresh validation.

For a method update, compare every bundled file and the complete inventory with
the immutable source. From `.agent-temper`, run `shasum -a 256 -c SHA256SUMS` or an
equivalent SHA-256 check, reject unexpected files/symlinks and inspect internal
links offline. Existing inventories do not establish all prose/anchor coverage.
Keep consumer extensions outside the immutable bundle. A finite issue, source/
compatibility review, checks and separate review precede pin replacement.
Classify findings using the pinned [extension rules](../../.agent-temper/docs/reference/extensions.md).
Sanitize any authorized public upstream proposal; do not copy private source or
sensitive evidence into an issue. An upstream change updates no consumer automatically.
