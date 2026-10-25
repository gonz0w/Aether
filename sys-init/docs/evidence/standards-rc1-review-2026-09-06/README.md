# Unpublished RC1 / ADP-03 review evidence

2026-09-06. Documentation-only sys-init review; no release adoption.

- `candidate/` retains the exact archive, external metadata and entry README.
  The copied verifier checked archive/manifest/source identities before extraction.
- `ADOPTION.md` is the separately captured ADP handoff; `identity.json` pins inputs
  and existing local release lock bytes. These remain review inputs, not runtime pins.
- `reviewed-sources/`, `clause-table.md` and `clause-matrix.json` support 177
  qualified clause dispositions. `review-validation.json` verifies their references.
- `local-snapshot/` and `checkout-before.json` bind the inspected dirty checkout.
  `prior-native-context/` retains identity summaries for prior local 175-case work;
  it is not a new native run, an archive of every raw result or release acceptance.
- `commands.json` and logs retain candidate checks, the failed mandatory renderer
  check (missing mmdc), and all nine passing local gates. Candidate example lint
  availability is not a sys-init lint gate. No dependencies were installed.
- `adoption.json` and `owner-review.json` preserve pending acceptance. No reviewer
  identity, exception approval or publication authorization is fabricated.
- `validation/` retains the complete local gate report/logs. This review does not
  change or requalify runtime code, kernel contracts or post-R1 features.

`sha256.json` inventories this evidence directory. Current Experience, Foundations
and Distribution v0.1.0 pins and vendored releases remain unchanged. Sibling sources
are only read. Existing uncommitted native work is excluded from the review commit.
