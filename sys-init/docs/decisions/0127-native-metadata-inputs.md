# 0127 — Native metadata file and manifest validation

BG-056 host slice, 2026-09-07. Require ordinary catalog/manifest files without
symlink components at/below the supplied root. Use bounded nonblocking reads,
check descriptor identity before reading and metadata after, and close on failure.
Keep the 4 MiB metadata limit. Hash and parse the same captured manifest bytes.
Validate the whole manifest before payload hashing: nonempty object, at most
10,000 normalized relative names, bounded text and lowercase SHA-256 values.
Reject duplicate keys, non-finite values and nesting above 32 levels.

Current manifests peak at 167,504 bytes/1,510 entries. Payloads remain under their
existing reader in this slice; do not apply metadata limits to large artifacts.
Test FIFOs/links, malformed matching-pin manifests, path/digest/count errors,
controlled replacement and same-byte hash/parse. Run focused and aggregate checks.
Preserve catalog, historical evidence and release pins. E-01–08 scope is host
metadata verification, not native acceptance or atomic filesystem snapshots.
Receipt validation, payload file policy/bounds and final consistency remain open.

Validation: 37 native-harness tests and all ten gates pass in run-5_9vk5jd.
Native audit stdout, catalog bytes and 24 native inputs are unchanged. Four manual
commands pass. Current largest listed artifact is 3,653,632 bytes; payload read
policy remains a separate follow-up. Evidence:
../evidence/native-metadata-inputs-2026-09-07/README.md.
