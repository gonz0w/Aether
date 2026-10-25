# Simplicity extension adoption

Adopted 2026-09-07 at the maintainer's request, prospectively for new and touched
first-party design, code, tooling and process. This is an **unreleased process
snapshot**, not a published Coding release, frozen RC1 content, or the four-profile
2026-09-05 approval receipt. Existing reviewed Coding v0.1.0 guidance and released
Foundations, Experience and Distribution pins remain unchanged.

Source: Aether-standards `drafts/coding-v0.2.0` at revision
`049fa158c1b9e799c799a0713a418601d4885c2e`. All four source files and SHA256SUMS match that revision.
Local [snapshot](evidence/coding-simplicity-2026-09-07/standards/README.md),
[manifest](evidence/coding-simplicity-2026-09-07/standards/SHA256SUMS):
`8c3d8095acc9b6283a5f6970bc4ce6e7e4646a04fb759f8cf2940ed494cbeff8` (SHA-256 of the manifest bytes).
The source revision establishes provenance, not independent approval. Builds and
tests do not consult the mutable sibling repository.

## Adopted scope

| Clause | Local application |
| --- | --- |
| SE-01 | A substantial change names the current boot, supervision or shutdown requirement. Shelved lifecycle machinery is not a v1 dependency merely because it is on the backlog. |
| SE-02 | Identify the specific borrowed idea and required surrounding mechanisms; compare direct implementation and maintained components where relevant, preserving upstream terms. |
| SE-03 | Prefer coherent responsibilities, explicit ownership/state and readable failure paths. No arbitrary length limits or removal of correctness/authority checks. |
| SE-04 | Count protocols, retained state, dependencies, operations and review/evidence steps as well as code. Reuse the existing review and backlog; retire obsolete paths only through scoped compatibility review. |
| SE-05 | Answer the three questions in the existing substantial-change description. Routine small fixes retain proportionate explanations. |

AGENTS records the principle; CONTRIBUTING routes contributors to the existing
QUALITY-PROCESS review. The snapshot's template is guidance for that review, not
a new required form. No runtime refactor, feature removal or new conformance
framework is part of adoption. No scoped exception is requested.

## Scoped assessment and next real change

This adoption's responsibility is contributor guidance. Control flow remains the
existing contribution/check workflow; state adds one immutable draft snapshot and
its provenance. A hash mismatch blocks adoption rather than silently updating the
snapshot or a released pin. Cost: four short shared documents and this disposition;
no new daemon, API, runtime dependency or parallel review system.

Simpler alternative: keep only the existing informal “small, understandable” goal.
We choose the existing review with three explicit questions because that goal did
not prevent the recent expansion of lifecycle machinery. Complexity removed now:
none in runtime code; this adoption prevents a second review process and makes
future complexity accountable. Passing checks does not prove the implementation
simple, elegant or conformant.

Apply SE-01–05 next to the planned two-service startup/shutdown composition
(current work item BG-065), in its existing change description. The scoped design
assessment to confirm before implementation is: one coordinator owns ordering;
use direct startup and reverse stop/cleanup flow; keep current instance/desired
state and bounded attempts; distinguish stop acknowledgment, observed termination
and cleanup, retaining unresolved resources/errors. Compare this with importing
the generic event/effect journal. Prefer the direct path if it meets the actual
scenario; do not claim it implemented or approved by this process update. Record
whether any current abstraction or duplicated path can actually be removed.

Existing complexity findings are triaged in BG-056 under SE-SI-01/02. Essential
boot/supervision/shutdown remains the focus; general history, recovery, advanced
activation and other-platform expansion remain shelved. The next implementation
review and independent review remain outstanding, not fabricated sign-offs.

## Verification

[Verification record](evidence/coding-simplicity-2026-09-07/README.md) records all four file
hashes, manifest identity, released-lock preservation and local check outcomes.
When updating this adoption, verify SHA256SUMS and every listed local file before
acceptance, record the new provenance separately, and rerun existing process
checks. Never rewrite this snapshot to accommodate a later draft. The quality
inventory links this record; its reference check is not a simplicity evaluator.

## First application — BG-065

The next-change review above has now been applied in BG-065's existing description
and [component reference](SIMPLE-SERVICE-PAIR.md). It chooses direct ordering over
the generic journal, names fixed state and failure behavior, and preserves old
fixtures rather than claiming a speculative removal. This completes the first
scoped application, not independent review or implementation-wide conformance.
The four shared snapshot files, manifest and released pins remain unchanged.
