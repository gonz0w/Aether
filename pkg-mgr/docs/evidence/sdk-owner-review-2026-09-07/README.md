# SDK owner material review

Read-only verification and local design response, 2026-09-07. See
[review](../../SDK-OWNER-REVIEW.md) for selected scope, compatibility issues and gates.

verify.py retains the exact inspection command source; it reads the userland-owned
bundle, validates the manifest and each path/type/mode/size/hash, matches all SDK
inputs and compares COPYRIGHT to the pinned archive member without extraction.
verification.json records observed inputs and results. This was a one-off material
review, not a new supported command or executable package harness. No preparation
script, compiler, package stage/import or native workload was executed.

Documentation-only checks are retained in checks.json. Existing package runtime,
release pins and sibling bytes were not changed. Unrelated dirty Origins work
remains outside this review's commit. Independent technical/maintainer acceptance
and SDK-01–08 are not claimed.
