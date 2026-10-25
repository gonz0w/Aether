# Quality record reference evidence

Decision 0115 adds docs/QUALITY-RECORDS.md: seven inventory fields, surface/gap
records, snapshot manifest, reference resolution/lifetime, and result/failure
contracts. It explicitly distinguishes referenced files from executed tests,
owner labels from independent approval and draft snapshots from release pins.
The actual quality-check success field set is verified in review.json.

All six quality tests pass: three existing command/current-record/mutation tests
and three new record tests. New controls reject an empty manifest despite a
matching digest, traversal and symlink references escaping the snapshot root,
unsupported layer and missing test file. The positive multi-layer fixture checks
exact surface/open-gap counts and result shape. No named fixture tests or tools
are executed by the quality reader itself.

All ten repository gates pass in out/checks/run-__pahll1, retained in validation/.
The quality reader bytes, reviewed snapshot location/pin and all 24 native inputs
remain unchanged. Quality inventory additions reference the new local guide,
decision and tests. No native implementation, sibling, released/vendored bytes
or historical evidence changed; no native execution is claimed. No failed
validation attempt occurred.

Remaining BG-056 findings: strict bounded JSON/schema/type validation, explicit
ordinary-file/symlink rules, snapshot inventory closure and stable identity
between hashing/parsing. Unlisted snapshot files, permissive parser behavior
and non-snapshot reference existence are documented limits, not public ingestion
semantics. Independent technical/reader approval, freshness policy and installed
reference work remain pending. This local reference is not a shared standard.
