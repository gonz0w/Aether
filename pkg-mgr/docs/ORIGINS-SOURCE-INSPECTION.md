# Origins source-record inspection — OC-H2

Experimental host development tool, 2026-09-06. This reference owns the local
inspection interface. It does not amend origins-source-v1, register a shared
standard, select a base package or add a package-manager runtime dependency.
Original work: SPDX-License-Identifier: BSD-2-Clause.

## Use and result

From the checkout, with the existing Python 3.10+ development interpreter:

```sh
python3 tests/origins_source_record.py --help
python3 tests/origins_source_record.py --version
python3 tests/origins_source_record.py fixtures/origins-records/source.json "$(cat fixtures/origins-records/source.sha256)"
python3 tests/origins-source-records.py
```

The first inspection example uses a synthetic record and externally retained pin.
Referenced object digests are placeholders; no object, license, reviewer or SDK
is accepted by this fixture. Never calculate a new expected digest from a changed
untrusted record merely to make inspection pass.

The inspector reads one regular file and produces one canonical ASCII JSON result
on stdout, with exactly one final LF. It writes no cache, package, trust or recipe
files. Origins, Git, network, shell and make are never invoked by the inspector.
The test driver writes only private test inputs/evidence. No inherited locale changes
JSON semantics. Input ancestors must be stable and caller-controlled; the final
component rejects symlinks, special files and multiple hard links. This is not a
hostile same-UID filesystem isolation guarantee. No arbitrary archive is extracted.

Exit 0 means inspection completed. Exit 2 means pin/format/profile rejection; exit 1
means input/output I/O failure; exit 64 means usage error. --help and --version
return 0 on normal output delivery. Signals retain interpreter/OS behavior; no
mutation recovery is needed because inspection has no authoritative writes.
Failure emits no successful report; failed delivery can leave partial stdout and
consumers must check exit status before using it. Diagnostics use plain ASCII
[BLOCKED]/[FAILED] and PKG-ORIGINS identifiers on stderr, without echoing input text.
This development command is not a new bin/pkg-mgr subcommand or installed manual.

## What is validated

The exact inspected proposal is retained as SOURCE-RECORDS.md.txt in
[the evidence inputs](evidence/origins-source-inspection-2026-09-06/README.md).
Its schema has 17 required top-level fields: schema, package, version, revision,
required_features, inputs, recipe, patches, helpers, options, dependencies, sdk,
build, host, target, licenses and evidence. No extra fields are accepted.

The Python standard-library JSON parser owns syntax and duplicate-key hooks.
A bounded pre-scan tracks strings/escapes solely to reject container depth above
eight before JSON parsing. Read at most 1,048,577 bytes to detect the 1 MiB limit;
fstat size rejects oversized regular files before reading. Storage latency and
concurrent privileged writers are outside this bound. Tests impose five seconds
per subprocess; the ordinary whole-suite watchdog supplies its existing deadline.

Validate ASCII, no NUL/control/DEL decoded strings, printable string lengths,
unsigned integers up to 2^53-1 and no booleans/null/floats/constants. Detect duplicate
keys before dictionary construction. Check the SHA-256 of original bytes against
the supplied canonical lowercase digest. Require canonical bytes: ASCII-sorted
keys, compact separators, only required quote/backslash escaping, ordered arrays
where specified and one LF. Never rewrite bytes and then claim the old pin matched.
Preflight size/depth/encoding errors can precede hash mismatch; identity is checked
before schema interpretation. Canonical equivalence is not upstream authentication.

Validate field types, exact nested keys, array/string counts, namespace/name tokens,
lowercase logical path grammar and input order. Reject duplicate paths, file/ancestor
conflicts, absent source or wrong recipe count, wrong-kind/unlisted patch/helper
references, invalid or duplicate options/dependencies/licenses/evidence, malformed
object references and unknown schemas/features. Ordered patches retain their order;
helpers and other declared sorted lists must already be sorted/unique. Object sizes
remain 0..1 GiB per the proposal. Repeated digests with conflicting sizes reject
locally as reference-conflict. No content read or graph traversal follows a reference.

The baseline supports no required_features. Origin text remains an inert string;
its VCS meaning and the requirement for upstream_revision on VCS sources cannot be
proven from this untyped field. Profile names and license expressions are validated
syntactically, not approved. Empty upstream_revision is structurally permitted;
publisher/typed-provenance agreement is required before semantic source admission.

## Report schema

`pkg-origins-inspection-v1` contains exactly these deterministic fields:

| Field | Value |
| --- | --- |
| schema | pkg-origins-inspection-v1 |
| status | inspection-only |
| record_sha256 | Digest of the original validated bytes |
| package, version, revision | Validated descriptive values, preserved exactly |
| input_count, dependency_count | Array counts; not resolved package counts |
| referenced_object_count | Unique directly referenced hashes, not recursive closure |
| byte_handoff | within-16-mib or over-16-mib based only on directly declared sizes |
| closure | unresolved |
| profiles | unresolved |
| eligibility | not-evaluated |

A within-limit report does not prove missing SDK/evidence objects or transitive
sources fit the store. No signer, freshness, local selection or installation right
is represented. Required report fields are not a grant that callers may forge.

Rejection identifiers: PIN-INVALID, LIMIT-EXCEEDED, FORMAT-INVALID, IDENTITY-MISMATCH,
DUPLICATE-KEY, NONCANONICAL, UNSUPPORTED-SCHEMA, UNSUPPORTED-FEATURE,
ORDER-OR-DUPLICATE, REFERENCE-CONFLICT, PATH-CONFLICT, FILE-TYPE-INVALID,
IO-ERROR and USAGE, each prefixed PKG-ORIGINS-. Diagnostics omit parser exception
text to avoid reflecting hostile source strings. Fix the record/pin or inspect
underlying file access; never interpret a missing tool or timeout as format denial.

## OC-01–06 disposition for this boundary

| Finding | Implemented inspection choice | Still required before admission |
| --- | --- | --- |
| OC-01 identity | Preserve namespace/name; no local PKGNAME generation | Explicit collision-checked local selection mapping |
| OC-02 paths | Validate existing lowercase grammar; never rename/materialize | Origins must decide preserved paths versus labels and case-sensitive materialization |
| OC-03 sizes | Validate 1 GiB schema ceiling; flag over-16-MiB direct references | Complete measured closure and agreed transfer budget |
| OC-04 roles | Validate build/target and uniqueness by package; no graph resolution | Agree dual-role and cross-toolchain semantics without dropping either dependency |
| OC-05 opaque records | Validate reference syntax/size consistency only; always unresolved | Versioned release-map/SDK/target/review formats and actual matching consumer evidence |
| OC-06 modes/invocation | Never create a recipe tree, set modes or execute code | Explicit entry-point/materialization contract and separate execution authority |

This resolves how inspection handles each finding without silently changing the
producer format. It does not close the broader OR-02/04 adoption findings. A typed
provenance field or reviewed origin scheme is an additional proposal for origins,
not a field invented in this parser. OC-07/08 trust/time/recovery/profile acceptance
remains separate. No sibling or immutable standards bytes were modified.

## Implementation choice and validation

Python's existing development standard library supplies JSON and SHA-256; no new
third-party package, runtime Python requirement or custom JSON grammar is selected.
A native/runtime parser needs its own bootstrap, resource and target review. Update
or remove this inspector with the development tools after producer format revisions;
retain old evidence, and never silently refresh an input pin after a failure.

The normal gate runs tests/origins-source-records.py. Evidence retains exact inputs,
expected labels/statuses, stdout/stderr, unchanged input/sentinel checks and initial
successful attempts. The corpus tests semantic failures, escaped strings/brackets,
inert shell text, size/depth limits and real FIFO/link/output-failure controls.
It is bounded regression evidence, not general fuzzing or hostile filesystem proof.
Independent reviewer acceptance, complete bootstrap closure and runtime trust remain
unproven. See [consumer review](ORIGINS-CONSUMER.md) for the broader contract.
