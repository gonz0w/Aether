# 0115 — Quality inventory field reference

BG-056 documentation/contract slice. Document quality-inventory top-level,
surface/gap records, pinned snapshot manifest and success/failure shapes. Explain
reference existence versus executed coverage and review ownership versus
independent approval. Keep checker, snapshot and native bytes unchanged.

Add focused cases for an empty manifest with a matching digest, escaping
manifest references, accepted layer/count reporting and missing referenced tests.
Existing CLI, omissions, duplicate-ID and changed-snapshot cases remain. Run all
gates and retain source identities. Follow-up: strict bounded schema/JSON parsing,
ordinary-file/symlink policy, snapshot inventory closure and stable input identity.
These are local review inputs, not a new shared standard or native API.

Validation: all six quality tests and all ten gates pass in
out/checks/run-__pahll1. The real report matches the documented field set. Reader,
reviewed snapshot pin and all 24 checked native inputs remain unchanged.
