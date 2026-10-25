# pkg-mgr rc1 / ADP-04 review evidence

Review date: 2026-09-06 (America/Denver; command timestamps are UTC).
[Clause matrix and findings](../../STANDARDS-RC1-REVIEW.md) own interpretation.
This bundle is review evidence, not a vendored release or runtime dependency.

## Inputs

- candidate-bundle.tar.gz, candidate-ARTIFACT.json and candidate-README.md.txt retain
  the unpublished kit. The archive contains its own full source manifest/provenance,
  license/notices and content approval receipt. Preserve their bytes and terms.
- source.json records the exact clean standards HEAD and five inspected entry-point
  hashes. ADOPTION.md.txt and check-candidate.py.txt preserve external handoff/checker
  inputs. The checker was read before execution; it verifies before extracting into
  temporary storage and executing the copied offline checks. No sibling file was edited.
- inputs-before.json records pkg-mgr HEAD, existing dirty status and hashes of tracked
  and untracked inputs before this review. This includes pre-existing Origins work,
  which is not part of the review commit. Hashes identify input bytes, not authenticity.
- approval-verification.json records 93 matching approval-receipt file digests. The
  maintainer's standards-content approval is distinct from this engineering review.

## Selection and outcomes

Oracle: exact candidate inventory and current pinned bytes verify; documentation
references/syntax and configured whole-shell lint succeed; all three manuals lint,
render and resolve in an owned staged host layout. Forbidden outcomes: changed release
pins/vendor bytes, silently promoted runtime/reviewer claims, sibling edits, or staging
unrelated work. No behavior change requires a new runtime test.

checks.json retains commands, timestamps, platform, per-command deadlines, exit statuses
and log hashes. Candidate, standards, development-lint and required manual checks passed.
The candidate check uses --run, not --strict: available pilot tools may run, but required
candidate sanitizer/diagram-render qualification remains standards-owner work. Neither
mode is independent review. manuals/ retains actual rendered outputs, curated examples
and its tool/source/result identities. No visual or independent reader sign-off is
inferred from renderer success. Its compiler-dependent binary example reports NOT RUN.

Final documentation checks and pin/source preservation are recorded separately after
editing. Full runtime/native suites, compiler-dependent examples and independent reader
walkthroughs were not rerun. Earlier component evidence remains valid only for its
original exact inputs/scope; it does not qualify an assembled Aether release.

adoption.json and owner-review.json use the candidate's pending record templates.
The new release is null and owner reviews are empty. Ranges in the Markdown matrix
are expanded in these summaries; profile-qualified Markdown disambiguates DS IDs.
These records are not completed adoption and do not update any pin.
