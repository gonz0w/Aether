# Conflict-guard layout build evidence

Decision 0088, 2026-09-06. No new native execution or runtime adoption.

`study.py` records the bounded attribute-only search over retained 0087 revisions
5 and 7. `matrix/` retains all 16 source snapshots and 80 build commands/results,
logs, maps and any generated outputs. `matrix/results.json` reports study
completion, not acceptance: no variant fits all five cases. Source and tool
identity checks are in the comparison records. `research-inputs/` contains hashed
sibling and consumer snapshots; these are review inputs, not runtime pins.
`research-inputs.json` gives source hashes and contextual sibling HEAD identity
without claiming that checkout was clean. `adoption/` retains final local records;
`validation/` retains the development gate results. `sha256.json` seals this bundle.

See ../../research/NATIVE-CONFLICT-GUARD-LAYOUT.md for interpretation and
../../research/NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md for the unaccepted handoff.

Validation: all nine development gates pass in `out/checks/run-s3ucn1zi`,
with no skipped gates and unchanged checked sources. Independent artifact review
confirms that only the three requested inline attributes vary, every mapped extent
matches the .text section size, and all 78 rejected links contain the size-limit
diagnostic. All eleven live consumer inputs and pinned compiler inputs still match.
No native case executed; the 151-case checkpoint and historical native audit remain
unchanged. Evidence, gate logs and host sample artifacts are retained under
`docs/evidence/conflict-guard-layout-2026-09-06/`.

`technical-review.json` records the independent attribute, map and failure checks.
Compiler warning logs are retained; no warning-free build claim is made.
