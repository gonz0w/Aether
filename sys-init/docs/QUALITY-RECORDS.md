# Quality inventory and reviewed-snapshot records

This is the field reference for [quality-inventory.json](quality-inventory.json)
and [check-quality-process.py](../scripts/check-quality-process.py). Read it with
[QUALITY-PROCESS.md](QUALITY-PROCESS.md) and the
[command manual](man/sys-init-check-quality.1). These are trusted local planning
and evidence references. Passing the checker does not establish executed tests,
native conformance, independent approval or release readiness.

## Inventory fields

The maintained top-level object has seven fields:

| Field | Maintained representation | Actual reader behavior |
| --- | --- | --- |
| `schema` | `sys-init-quality-inventory-v1` | Exact equality required |
| `scope` | Description of the inventory boundary | Required bounded string |
| `snapshot` | Relative directory containing reviewed draft sources | Appends `/SHA256SUMS.json`, then validates that file reference |
| `snapshot_manifest_sha256` | SHA-256 of the exact manifest file bytes | Exact comparison before loading the manifest |
| `process` | Nonempty array of local file references | Every destination must exist within the checkout |
| `surfaces` | Nonempty array of coverage records | Checked as described below |
| `gaps` | Nonempty array of open-work records | Checked as described below |

Decision 0116 requires exact top-level and surface field sets and the gap shape
below. Missing/unknown fields and wrong types reject before local-reference
traversal. JSON duplicate keys and non-finite constants reject. Metadata remains
syntactic data, not authenticated evidence.

## Coverage surfaces

| Field | Meaning | Enforced condition |
| --- | --- | --- |
| `id` | Stable local surface ID, currently Q-* names | Nonempty bounded string, unique across **both** surfaces and gaps; no Q-/G- prefix is required |
| `owner` | Responsible maintainer | Nonempty bounded string; not an identity lookup or signature |
| `status` | Scope of the claim | Exactly `experimental`; `conformant` is rejected |
| `layer` | Model, host or native target evidence category | Exactly `model`, `host` or `target` |
| `reference` | Canonical explanation/specification | Existing local file |
| `tests` | Named test source references | Nonempty, with every destination an existing local file |
| `oracle` | Expected result or rejection description | Nonempty bounded string; no semantic verification |
| `evidence` | Local retained result, decision, specification or catalog | Existing local file; its schema/content is not consumed here |
| `stage` | When the contributor should run/review the checks | Nonempty bounded string; no scheduler or stage vocabulary enforcement |

The checker does not import test files, count test cases, run commands or compare
evidence with current runtime inputs. Duplicate paths within tests/process lists reject.
A specification can be an evidence reference in the current inventory without
thereby becoming an execution witness. Keep that distinction in the owning
surface reference and change-specific evidence. Use aggregate/native checks to
establish the appropriate execution layer.

## Open gaps

Each maintained gap has `id`, `topic`, `status`, `owner`, `backlog` and `milestone`.
IDs share the surface namespace. Owner, topic and milestone must be nonempty
bounded strings;
status must be exactly `open`. Backlog must identify an existing local file.
Optional `reference` and `review_evidence` fields also require normalized local
file paths and existing destinations. They do not establish independent review.
Topic and milestone describe remaining work, not machine-enforced acceptance
criteria. Empty gaps are rejected by the present reader, so this inventory does
not currently model a fully closed release state. Closing all gaps requires a
separately reviewed format/process change, not removing the list to obtain pass.

## Reviewed snapshot manifest

The manifest is an ordinary JSON object mapping snapshot-relative file names to
SHA-256 strings. Its own complete byte digest is pinned by the inventory before
parsing. It must contain 1–1,000 entries with normalized relative names and lowercase
SHA-256 strings; every listed file must resolve inside the
manifest's directory and its bytes must match the listed digest.

Digest equality is not signature verification, freshness or authorization.
Whitespace changes to the manifest change its pin. Whitespace changes to a
listed source change its digest. Decision 0117 requires the tree to contain exactly the listed files plus
SHA256SUMS.json. Unlisted or missing files reject. Ordinary directories may
exist, including empty ones, but total files/directories are limited to 2,000.
Symlink and special entries reject; traversal does not intentionally follow links. Duplicate JSON keys reject. The manifest is read into a bounded buffer once;
its digest and parsed content use those same captured bytes. Decision 0117 repeats tree membership and listed-file digest checks and compares
manifest/inventory bytes before success. This is not an atomic snapshot.

The retained reviewed snapshot is evidence of drafts inspected at a particular
point; it is not a published standards release or runtime dependency. Keep its
historical bytes immutable. A future review gets a new snapshot and explicit
inventory/pin update with its own evidence. Never rewrite old evidence to make
current checks pass. Release pins remain separately governed by STANDARDS.md.

## Local reference rules and lifecycle

`local_file(root, name)` requires a nonempty string, rejects absolute paths and
`..` components, resolves it under root and requires an existing file whose
resolved path remains inside root. Within-root symlinks in general references are currently accepted;
symlinks escaping root reject. Snapshot path components from the checkout root
to the manifest and all entries within the snapshot must not be symlinks. The validated inventory/manifest paths reject dot/parent/empty segments and
backslashes. The internal local_file helper itself still uses Python Path
normalization if called directly. Snapshot references
use the manifest directory as root; process/coverage/backlog references use the
checkout root. No URI lookup or network fetch occurs.

Reference contents outside the snapshot are not hashed by this checker, and the
inventory bytes are compared again before success under decision 0117. The aggregate has a separate
source-identity check, which does not turn these reads into an atomic snapshot.
Decision 0116 limits each JSON input to 1 MiB, nesting to 32 levels and each
list/manifest to 1–1,000 entries. Strings contain 1–4,096 Unicode characters,
must encode as UTF-8 and exclude ASCII controls/DEL. There is no standalone
filesystem I/O deadline or bound on all referenced file sizes.
Tests exercise trusted temporary directories; this is not a public ingestion
boundary or protection against hostile concurrent filesystem changes.

## Results, failures and coverage

Success prints exactly the fields `schema` (`sys-init-quality-check-v1`),
`result` (`pass`), `scope` (`record structure and reviewed bytes only`), `surfaces`
and `open_gaps`. Counts are array lengths, not test counts or reviewed-line
coverage. The report has no timestamp, signer, source hash map or approval field.

The CLI catches OSError, ValueError, KeyError and TypeError, writes an ASCII-
escaped diagnostic on stderr and exits 1. It does **not** emit failed JSON on
stdout. Other exceptions or abrupt termination may bypass that diagnostic.
Help/version exit 0; invalid usage exits 64. Preserve stdout, stderr and exit
status; absent output is not success. The command does not write or delete files.

Existing [quality-process tests](../tests/test_harness_quality_process.py) cover
CLI streams, current records, missing sections/owners/oracles/references,
unsupported status, cross-list duplicate ID, changed snapshot source and changed
manifest bytes. Additional [record tests](../tests/test_harness_quality_records.py)
cover matching-pin empty manifests, escaped snapshot references, layer/count
reporting and missing test destinations.

All inputs and references must be ordinary files, with no symlink components
at or below the supplied checkout root. General references are existence checks;
their content is not read or size-limited. Inventory, manifest and snapshot payload
reads are capped at 1 MiB per file. Opens use nonblocking mode and no-follow where
available; descriptor type/device/inode must match the preceding path check.
Size and mtime are checked again after reading, and descriptors close on failure.
The [input tests](../tests/test_harness_quality_inputs.py) exercise these bounds.

BG-056 follow-ups: filesystem I/O deadlines and remaining record/API families. Snapshot file closure and final inventory/manifest
byte checks now apply, but changes restored before comparison, hostile directory
replacement races and mutation after the final check remain outside the guarantee.
These checks do not establish stable identity for every referenced input. Independent technical/reader review, snapshot
freshness policy and remaining record/API families stay open. This reference
records current behavior without endorsing permissive parser behavior as a
public contract.
