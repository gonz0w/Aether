# Package documentation review procedure

For Cam and a representative package-manager reader. Status: **not performed**.
Review exact candidate inputs in an owned disposable environment. The author must
not coach the reader through missing steps. An agent-written checklist or successful
renderer cannot supply actual reviewer identity, observations or approval.

## Public surface ownership

| Surface | Canonical reference | Coverage and remaining review |
| --- | --- | --- |
| list, owners, verify, orphans, files, deps, rdeps | [pkg-mgr(1)](../man/pkg-mgr.1), [pkg-state(5)](../man/pkg-state.5) | Names/state keys and fixtures checked; complete semantic/error review pending |
| export, import, recover, preflight, prepare, finish | [pkg-mgr(1)](../man/pkg-mgr.1), [pkg-binary(5)](../man/pkg-binary.5) | Curated examples and transaction fixtures; consequential actions and recovery prerequisites need reader review |
| --root, --format, --color, --plain, --quiet, --help, --version | [pkg-mgr(1)](../man/pkg-mgr.1) | Seven help/manual names checked; all defaults/behavior/accessibility not certified |
| Records, world, ordinary modes and build evidence | [PACKAGE-STATE](PACKAGE-STATE.md) | Schema and world cases; full case-level format mapping pending |
| Bundle, descriptor, target and pinned recovery | [BINARY-PACKAGE](BINARY-PACKAGE.md), [IMPORT-RECOVERY](IMPORT-RECOVERY.md) | Byte/type/path and recovery cases; no remote authenticity or target durability |
| Local configuration and retained replacement | [REPLACEMENT-POLICY](REPLACEMENT-POLICY.md), [UPDATE-PREFLIGHT](UPDATE-PREFLIGHT.md) | Three-way/fault cases; reader must distinguish preflight, prepare, finish and unknown outcome |
| Contributor setup/build | [CONTRIBUTING](../CONTRIBUTING.md), [BUILD-FIXTURE](BUILD-FIXTURE.md) | Host tests exist; uncoached clean-checkout walkthrough pending |
| Native and development-only helpers | [development inventory](development-inventory.json) | Separate experimental subsystem scope; not installed public commands or native package qualification |

This table routes readers; it does not duplicate or replace references. Metadata
helpers, recipe options and developer commands need complete coverage before being
advertised as public interfaces. Historical evidence and literal protocols remain
unchanged. Full version-bound publication inventory remains incomplete.

## Walkthrough and record

1. Record reviewer, UTC date, exact source/artifact digest, dirty state, platform,
   tools, authority, deadline and goal. Distinguish technical review from reader testing.
2. Follow CONTRIBUTING and BUILD-FIXTURE from the documented entry point without
   unpublished instructions. Record every command and observable result.
3. Use help/manuals to inspect the disposable root, diagnose an invalid argument
   and failed verification, and find plain-output instructions.
4. Follow supplied import/preflight/recovery examples in owned private roots only.
   Record whether the docs explain prior-state preservation, pending intent, required
   pins and safe retry. Use existing fixture procedures; do not invent destructive
   crash injections or touch a real prefix.
5. Inspect all three manuals at 60/80 columns and in HTML for wrapping, copyable
   commands, statuses, references and lookup. Separately check packaged Aether
   lookup when an actual target package exists.
6. Record obstacles, missing prerequisites, ambiguous wording and mismatches with
   issue IDs. Repeat affected steps against corrections. Leave acceptance pending
   until the actual reviewer supplies a decision.

Retain logs, skipped/blocked steps, corrected revision, reviewer identity, scope,
observations and decision/date. Link the real record from STATE and the candidate.
Cam's assignment and authorization to improve the project are not completed review.

Inventory any diagrams in release scope before publication. Each needs canonical
source, text alternative, pinned offline renderer/fonts and light/dark inspection.
No full Markdown-anchor, diagram or accessibility audit is claimed by this procedure.
Authoring/rendering tools remain development dependencies.

## Author preparation checkpoint — 2026-09-07

[The manual scope review](evidence/manual-scope-2026-09-07/README.md) aligns the
three active headers with experimental project scope and retains fresh rendering,
lookup and curated-example results. Its top-level Markdown inline scan found no
fragment references or diagram markup; alternate syntax and historical content
are outside that scan. This is preparation only. The walkthrough above remains
not performed; no reviewer identity or decision has been supplied.


## Scoped SDK document review; hands-on testing deferred

Cam's [actual SDK review statement](evidence/sdk-maintainer-review-2026-09-07/README.md)
is recorded. This resolves review of that documented scope; it is not the uncoached
manual/workflow walkthrough above. Cam deferred deeper testing until an ISO exists.
[The ISO package test card](ISO-PACKAGE-TEST.md) prepares that target slice without
claiming it ran. Do not request the same SDK document review again or broaden it
into all-format/native/release acceptance.
