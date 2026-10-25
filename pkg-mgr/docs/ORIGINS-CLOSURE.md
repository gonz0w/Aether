# Declared source closure — OC-H3 host-review profile

Experimental local producer/consumer proposal, 2026-09-06. This document owns the
pkg-mgr host-review formats below. They are not accepted origins publication formats,
a shared standard, a native target or a replacement for package state. No affected
owner or independent approval is inferred. Original work: BSD-2-Clause.

## Purpose and usage

OC-H3 connects a pinned local selection to a release map, source records, SDK/profile
and evidence manifests, then checks every object declared by the selected dependency
set. A source record still uses the reviewed origins-source-v1 syntax from
[OC-H2](ORIGINS-SOURCE-INSPECTION.md). Supporting schemas deliberately use
pkg-origins-review names until origins/userland agree a handoff.

```sh
python3 tests/origins_closure.py --help
python3 tests/origins-closure-cases.py
```

The test prints a retained .pkg-mgr-live-origins-closure-* directory. Its complete/
subdirectory contains a runnable private two-package example. Substitute its printed
absolute path as CASE, then use the checked fixture pin:

```sh
python3 tests/origins_closure.py "$CASE/objects" "$CASE/selection.json" "$(cat "$CASE/selection.sha256")"
```

The inspector never fetches, sources code, invokes make, builds, extracts, materializes
recipes, changes modes, installs or starts services. Recipe bytes deliberately contain
a shell-looking command; the test requires no command-created file or state change.
The examples use synthetic SDK and review inputs, not actual compiler/source approval.

## Record conventions

Every record is ASCII canonical JSON under OC-H2's syntax, integer/string/depth and
1 MiB metadata bounds. Reject duplicate/unknown keys and schemas. Fields below are
all required. Object references have exactly sha256 and size, with lowercase SHA-256
and an unsigned size at most 16,777,216 bytes. Metadata references additionally cap
size at 1,048,576. Source records may describe larger objects under OC-H2, but OC-H3
rejects their transfer; it never splits or truncates them.

Package IDs remain namespace/name. Tokens use OC-H2's lowercase token grammar.
Arrays described as sorted/unique must arrive that way. Reference identity always
binds original bytes; no URL or named-file fallback. No feature silently adds a new
schema. These schemas are scoped fixtures, not a new generic metadata language.

| Schema | Exact fields after schema | Rules |
| --- | --- | --- |
| pkg-origins-review-selection-v1 | release, roots, mapping | release is an object reference; roots is 1..64 sorted unique package IDs; mapping is 1..64 entries with package and local_name, sorted unique by package |
| pkg-origins-review-release-v1 | repository, profile, packages | repository is a 64-character digest label, not an authenticated enrollment; profile is a reference; packages is 1..64 entries with package and record reference, sorted unique by package |
| pkg-origins-review-profile-v1 | name, purpose, build, host, target | name is a token; purpose is synthetic-host-fixture; build/host/target must all equal name; native/cross-profile behavior is unsupported |
| pkg-origins-review-sdk-v1 | purpose, profile, inputs | purpose is synthetic-host-fixture; profile must equal the release's exact profile reference; inputs is 1..32 entries with name token and object reference, sorted unique by name |
| pkg-origins-review-evidence-v1 | kind, objects | kind must be synthetic; objects is 1..32 references sorted unique by digest; no reviewer/approval status accepted |

The SDK and evidence references in each source record must decode as these manifests.
Their inputs/objects are raw leaf bytes, not implicitly recursive SDKs or recipes.
Every source input, patch/helper (through the validated input lists), license text,
SDK input and evidence object is required. License expressions remain descriptive;
matching a license file does not establish redistribution rights.

The local selection pin is supplied externally. The release reference binds the
same exact catalog and profile consumed throughout the walk. Local names are explicit
lowercase tokens and globally unique in the selected set; never derive them by
stripping a namespace. The mapping must cover exactly the reachable packages: missing
or extra mappings reject. Unselected catalog records are not traversed or claimed
verified. Multiple roots and shared dependencies are allowed. No provider solver,
version ranges, automatic overlays, ambiguous roles or execution policy is introduced.

## Graph and object checks

Each dependency's reference must equal that package's release-map reference. Each
source record's package must match the map key. Dependencies retain build/target roles
and uniqueness rules from OC-H2. This profile is homogeneous: all records must match
the release's synthetic build/host/target tuple. It cannot settle general dual-role
or cross-compilation semantics merely by accepting their labels.

Reject missing packages/objects, conflicting reference sizes, content/size mismatch,
cycles, invalid mappings, unsupported profiles and schema mismatches. Bound traversal
to 64 catalog packages, 256 selected dependency edges, 16 package levels, 256 unique
objects and 32 MiB aggregate unique object bytes. A separate 64 MiB cumulative
read budget charges expected size plus one byte before every object read, including
repeated SDK/evidence references; exhaustion rejects as READ-LIMIT. This bounds
repeated I/O even when unique-object totals remain small. Count release/profile/source/SDK/
evidence records as objects; the separately bounded local selection file is outside
the object total. Repeated objects count once for resource totals, but requested bytes
are rechecked on reads. Metadata is bounded before parsing; raw leaf data is streamed
in at most 64 KiB reads, with at most expected size plus one byte read per verification.

Graph heights are retained for already visited dependencies: a shared node cannot
hide an excessive longest path simply because a shallower path reached it first.
The cycle guard precedes a back-edge reference comparison. The cyclic fixture uses
an inconsistent closing reference, not an impossible claim to have constructed a
cryptographic hash fixed point. Both cycle and reference mismatch are rejection
conditions; the fixture checks the documented cycle-first ordering.

OBJECTS is an owner-controlled 0700 directory, opened once with no-follow semantics.
Names inside it are canonical digest filenames opened relative to its descriptor.
Reject nonregular/multi-linked objects and final-component symlinks; FIFO opens are
nonblocking. Missing objects have a semantic rejection, while open/read/output failures
remain I/O errors. Caller-controlled stable ancestors and no hostile same-UID writer
are assumptions. No race-proof or power-loss admission authority is claimed. There
are no writes, so failures may produce diagnostics but cannot advance package/trust state.

## Output and errors

Success emits canonical ASCII JSON schema pkg-origins-closure-report-v1 with exactly:
status=declared-closure-only, selection_sha256, release_sha256, packages (sorted
package/local_name pairs), dependency_edges, object_count, object_bytes, sdk_count,
eligibility=not-evaluated, sdk_completeness=not-proven and base_admission=not-evaluated.
Object totals describe declared inputs only. This is not proof that a real compiler,
its host libraries, generated inputs or runtime dependencies were fully declared.

Normal --help/--version return 0. Inspection success returns 0; schema/identity/graph/
policy-boundary rejection returns 2; I/O failure returns 1; usage returns 64. Diagnostics
are plain ASCII on stderr with PKG-ORIGINS-CLOSURE identifiers, never untrusted parser
text. Rejection emits no successful report. Output failure can leave partial stdout;
callers must check status. Signals retain interpreter/OS behavior.

In addition to OC-H2 format errors, identifiers include OBJECT-LIMIT, METADATA-LIMIT,
CLOSURE-LIMIT, ROOT-INVALID, OBJECT-MISSING, DEPTH-LIMIT, DEPENDENCY-CYCLE,
PACKAGE-MISSING, RELEASE-MAP-CONFLICT, PACKAGE-CONFLICT, PROFILE-MISMATCH,
PROFILE-UNSUPPORTED, SDK-UNSUPPORTED, SDK-PROFILE-MISMATCH, EVIDENCE-UNSUPPORTED,
EDGE-LIMIT, READ-LIMIT, MAPPING-COLLISION and MAPPING-INCOMPLETE. References with inconsistent
sizes reject as REFERENCE-CONFLICT. No error is repaired by repinning or choosing a
replacement release. Correct the selected inputs and run a new explicit inspection.

## Owner decisions and next work

This is the concrete reviewable proposal requested by the maintainer, not invented
agreement. Origins must accept/revise release-map and object publication bindings;
userland must accept real SDK/target/admission evidence formats and the selected
base package closure; pkg-mgr must qualify local selection/current-policy authority.
Aether-standards owns shared source-profile/ownership changes. No messages, remote
publication, sibling implementation edits or shared pin changes occurred here.

Use this fixture to discuss exact required fields before replacing synthetic purpose/
evidence labels with real owner semantics. Real packages also need reviewed paths/
materialization, compiler/host closure and provenance/license evidence. Authenticated
TUF/time/state recovery remains OC-07/08 work. Neither record completeness nor source
hash identity is authorization to execute. Next handoff is a real owner-supplied
candidate and exact SDK/profile/review definitions against these demonstrated checks.

## Validation

`python3 tests/origins-closure-cases.py` constructs two source records with one explicit
dependency, a shared SDK/profile and all declared raw inputs, then runs the consumer
in separate processes. Variants cover build-role and explicit namespace mapping,
missing object classes, hash/map/identity/profile errors, source-role rejection,
cycles, depth including cached dependencies, edge/object/byte budgets, unsafe paths
and unchanged input/state trees. Each child has a ten-second budget; the normal
`sh tests/check.sh` gate supplies the existing 600-second group watchdog.

Python and standard-library JSON/SHA-256 remain development-only dependencies; no new
third-party parser or native runtime choice. Source inspection reuses OC-H2. Evidence
retains commands, exact dirty inputs, expected/observed results and original attempts.
See [OC-H3 evidence](evidence/origins-closure-2026-09-06/README.md). These are host,
synthetic declared-closure checks, not production, native or independent review claims.
