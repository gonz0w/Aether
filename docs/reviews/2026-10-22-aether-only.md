# Consolidated ownership and Aether-only product scope

Requirement: the maintainer consolidated kernel, userland, sys-init and pkg-mgr
into Aether and withdrew other-OS product support. Update active guidance,
acceptance and ecosystem navigation before the original checkouts are removed.
Standards, dist, installer, origins and the website remain separate repositories.

Allowed result: one system checkout and Aether-only runtime requirements, retaining
component policy/authority boundaries. Host tools and tests remain useful development
inputs; POSIX conventions and upstream platform source are not support promises.
Forbidden: editing immutable releases, approved draft bytes, historical evidence or
pins; deleting original checkouts; weakening authority/cleanup/target qualification;
claiming unexecuted tests or refactoring the runtime for this administrative change.

Owners: root integration, userland runtime/base, sys-init lifecycle, pkg-mgr
installation/trust; external standards/catalog, dist composition, installer,
origins and website guidance. Preserve unrelated dirty website work.

Test selection: affected offline standards, local guidance/inventory/link checks;
focused tests only if an executable path changes. Verify protected inputs against
pre-change hashes. No persistence guests or full runtime suites for prose changes.

Simplicity: retaining contradictory portability goals would require unnecessary
platform adapters and campaigns. Remove those goals and supersede old research
prompts instead of adding a compatibility framework. Keep existing working host
checks and first-party POSIX discipline. No new unsafe code, authority, dependency,
resource budget or runtime API is needed. Results follow after checks.

## Results

Active target/agent guidance, intent, backlog requirements, evidence-gap inventory
and current integration gates now use Aether-only product scope. Three obsolete
living research/gate pages retain their original text in component `docs/archive/`
with concise current replacements. Existing host regression code stays: inspection
found no active first-party per-OS sandbox runtime backends to remove. Upstream
platform sources, compiler target spellings and frozen evidence remain intact.

Standards' catalog and adoption page now route ADP-01–04 to Aether components;
the dated nine-owner audit remains unchanged. Standards, dist, installer, origins
and website entry guidance records the consolidation. Dist's snapshot example
uses `Aether/pkg-mgr`. Website scanner and drift commands share one explicit path
map; stable article/component identifiers remain. Component scans hash documents;
the Aether root scan records the shared Git history. No publication occurred.

| Scope | Executed result |
| --- | --- |
| Kernel guidance | `python3 -B docs/check-standards.py` and `python3 -B scripts/check_workflow.py` pass; 174 test groups inventoried |
| Userland | `python3 -B docs/quality/check.py` passes offline pins/inventory |
| Sys-init | `python3 -B scripts/check-quality-process.py` and `python3 -B docs/check-standards.py` pass |
| Packages | `python3 -B tests/check-development.py` passes syntax, 345 links and inventory; `sh tests/check-standards.sh` passes all three pins |
| Standards | `python3 -B tools/check.py` passes integrity, approved snapshots, navigation, dated adoption and rejection cases; optional Mermaid renderer not installed, no rendering claim |
| Dist | `python3 -B scripts/check-quality.py` and `python3 -B docs/check-standards.py` pass |
| Installer | `scripts/check_docs.py`, `scripts/check_inventory.py`, `scripts/check_standards.py` with Python `-B` pass |
| Origins | `python3 -B tests/check.py` passes offline pins/inventory/links and its bounded host tests |
| Website | Three focused consolidation tests and 18 existing updater tests pass; `python3 -B tools/check_docs.py` passes |

Independent comparison verifies 1,196 protected release/review/approved-draft/audit
files unchanged across the six repositories. 54 current navigation links into
Aether resolve; affected diff whitespace checks pass. No standards pin, runtime
ABI, authority, resource limit or native test requirement changed. Full runtime
suites and persistence guests were not selected for this administrative scope.

Attempt record: an initial root invocation mistyped `check_workflow.py` with a
hyphen and exited 2; the documented underscore command passed. The first website
documentation check rejected a sibling Markdown link because its offline checker
requires local destinations. Replacing it with a plain checkout reference passed;
no checker was weakened. Initial two routing tests passed before adding the drift
command's third case. No test failures were hidden or retried automatically.

Original checkouts remain untouched for the maintainer to remove. Unrelated
website edits remain outside this commit; only this task's routing/guidance hunks
are staged. Next runtime work remains root STATE's BG-073 initialization slice.

The three new website regressions also pass against the exact staged source
closure, isolated from the pre-existing dirty website implementation.

Ecosystem commits (local only; no push or publication):

- Aether-standards: `6868d990712707cc9b202c93e951612cef51c26f`
- Aether-dist: `56f149b1da2946c093b22f0db5e686ca53a94676`
- Aether-installer: `4b5e574e96b5bb1f90caa55c7708f10edb6622ed`
- Aether-origins: `3572a151e7a28ff43fda2ac2965821f7ca848592`
- Aethersys.org: `09f1463b322727d0b3aa8563c9bd9e9e61de805a`

Retired guidance archived from the pre-change commit (original bytes also remain
in Git; the research prompt’s date-line trailing spaces were removed to satisfy
the existing commit whitespace gate):

- `pkg-mgr/docs/archive/2026-10-22-cross-os-research.md`: SHA256 `a6ca098de31266dafaab6ef1ef271abac09798b1684f2bc1823003f769f4de45`.
- `sys-init/docs/archive/2026-10-22-integration-gates.md`: SHA256 `1f51403a36e6ec3b1712a52f4ab8c7e7c025e3e48aa2dea02816044989e6f71f`.
- `sys-init/docs/archive/2026-10-22-bg054.md`: SHA256 `b856d1a3e7c3222c6420ae68446815b31d2d6c7cafd5017073845c9086cbe675`.

The first root staging check rejected two inherited trailing spaces on the archived
research prompt’s date line. Removed those spaces only, updated its recorded hash
and kept original bytes in history; no commit hook or frozen input was changed.
