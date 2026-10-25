# Read-only SDK rebuild plan

2026-09-07. The experimental local helper implements the contract below, following
the [static-input witness](SDK-STATIC-BINDING.md). It inspects two private roots
and reports packages requiring requalification. This is not a released interface. No build, update, replacement, execution or service activation is
authorized by a plan. Existing commands and release pins remain unchanged.

## Inputs and trust boundary

The helper takes an installed private root, a candidate private root,
independently selected SHA-256 pins for both aether-musl-sdk package records and
the candidate SDK target profile. Invoke from the checkout:

```sh
sh mk/sdk-rebuild-plan.sh INSTALLED_ROOT CANDIDATE_ROOT INSTALLED_RECORD_SHA CANDIDATE_RECORD_SHA CANDIDATE_PROFILE_SHA
```

All three SHA arguments are independently selected lowercase SHA-256 values.
This internal helper has no bin/pkg-mgr dispatch or installed manual entry.
The candidate root must contain only the SDK package. Both roots must pass current
v2 state, world, graph, payload and mode validation, with no pending transaction.
The SDK must have no package dependencies. Reject v1 records and unsafe roots.

Verify both selected record pins from actual bytes. Validate the candidate's
manifest-bound target and receipts with the existing [SDK profile](SDK-PROFILE.md)
rules and supplied profile pin. Do not require equality with the installed profile:
a changed profile can require requalification too. This validates recorded identity,
not compiler compatibility, receipt truth, publisher authentication or admission.
A copied historical receipt does not qualify changed SDK bytes.

Use a caller-quiesced private snapshot. Record all installed package record hashes
and the world hash, and revalidate their inventory, bytes and verified payloads
before emitting a report. Detectable changes fail the operation. Rechecking does
not defeat hostile concurrent writers or establish an atomic snapshot; those are
unsupported. No plan is reusable apply authority, even when all its hashes match.

## Direct-consumer binding

Every installed package with a direct dependency on aether-musl-sdk must contain
one regular, manifest-bound file at
`usr/local/share/pkg-mgr/NAME/sdk-binding.kv`. NAME is the consuming package name.
The experimental first version has these seven rows in this exact order:

```text
format=sdk-static-binding-v1
sdk_package=aether-musl-sdk
sdk_record_sha256=HASH
input_receipt_path=RELATIVE_PATH
input_receipt_sha256=HASH
artifact_path=RELATIVE_PATH
artifact_sha256=HASH
```

HASH means exactly 64 lowercase hexadecimal bytes, not the literal placeholder.
Paths are relative to the consumer's stage, use existing state-schema path grammar,
and are at most 1024 bytes each. Both must name distinct regular files recorded in
that consumer's manifest, distinct also from the binding file. Compare their
hashes with both manifest rows and actual files. Reject symlinks and unsupported
entry types using existing private-root restrictions. Do not execute artifacts.

The binding is at most 4096 bytes, ASCII with one final LF, no CR/NUL, blank rows,
unknown or duplicate keys, alternate ordering, extra key/separator whitespace or
escapes. Spaces permitted by the state path grammar remain literal filename bytes.
Values are inert data; never source or evaluate them. Compare sdk_record_sha256
with the currently installed SDK record, **before** comparing the candidate.
Missing, malformed or stale direct bindings reject the whole plan, including an
unchanged candidate. There is no implicit exemption for a direct SDK dependency.

The input receipt is an opaque, hash-bound regular file, at most 1 MiB.
State verification streams all payload hashes before binding inspection; the
receipt limit applies before the planner separately hashes that bound input. Its internal
format and completeness remain the producer's responsibility. The planner proves
which bytes were recorded, not that every compiler, option, header, adapter or
archive was captured. This first version covers one artifact and one receipt per
consumer; broader producers need a separately reviewed format extension.
The experiment's JSON binding is not this format and must not be silently accepted.

## Selection and report

Compare complete SDK record hashes conservatively. Equal pins produce a valid
empty selection after all validation. Different pins select every direct consumer
and the entire reverse dependency closure of those consumers. This includes
non-world packages. Dependencies of selected packages are not selected merely for
being dependencies. Unrelated packages are excluded.

Report a package once, as direct if it has the SDK edge, otherwise transitive.
Walk with a visited set: diamonds deduplicate and cycles terminate. Report order
is bytewise package-name order under LC_ALL=C, not build order. Cycles are allowed
by the existing state graph; this report does not invent a scheduler for them.
Transitive packages need no direct SDK binding unless they also have the SDK edge.
Their selection is conservative requalification, not proof they require relinking.

Machine output is LF-terminated TSV, with literal tabs as separators:

```text
format\tsdk-rebuild-plan-v1
sdk-installed\tHASH
sdk-candidate\tHASH
candidate-profile\tHASH
world\tHASH
record\tNAME\tHASH
requalify\tNAME\tdirect\tHASH
requalify\tNAME\ttransitive\tHASH
```

The five header rows occur once in that order; record rows cover every installed
package in name order, then zero or more requalify rows in name order. HASH on a
requalify row is that installed consumer's record hash. The two example selection
rows illustrate alternatives, not mandatory rows. An empty selection still emits
the header and complete record inventory. The installed/candidate pins identify
metadata changes too; identical resulting ELF bytes never suppress selection.

Success is exit 0 with the complete report and empty stderr. Invalid arguments or
pin syntax return 64; invalid state/binding/profile, bound exhaustion, unavailable
or failed tools, I/O failure and detected input drift return 1. Validation failures
produce empty stdout and a plain diagnostic on stderr. Assemble output privately
before writing stdout; failed delivery returns nonzero but may have emitted a
prefix. Consumers must check status and discard incomplete output. No progress,
color or terminal control bytes occur in machine output. Preserve existing CLI
behavior; any future human renderer needs its own Experience review.

## Bounds, effects and cleanup

Initial planner limits: 1024 installed packages, 16384 dependency edges, 1 MiB per
package record, 16 MiB aggregate record bytes and 1 MiB world bytes. Check these
before graph processing. Binding limits apply before parsing; receipt limits apply before the planner
separately hashes the bound receipt (state verification already streams payloads). Exceeding a limit rejects the complete operation, never truncates it.
Payload verification streams file hashes; payload size affects elapsed time, so
these are metadata/memory bounds, not a runtime deadline or hostile-input sandbox.

Only process-owned, mode-0700 scratch outside both roots may be created. Keep
records, manifests, stage bytes/modes, world, pending state and unrelated sentinels
unchanged. Remove only owned scratch on normal exit and catchable interruption;
SIGKILL may leave scratch for inspection. No root locks, repair, journal, admission
marker or persistent plan cache are written. Planning needs read access, not root.

## Validation and remaining coverage

Use a POSIX shell helper and bounded AWK/plain-file processing consistent with
[package state](PACKAGE-STATE.md). No new runtime dependency is justified here.
The shell helper owns fixed namespaced diagnostics; its tests check selected exact
rejections and report bytes through real registration in disposable private roots.
The table remains the acceptance checklist; coverage limits are recorded below.

| Planned case | Independent oracle / forbidden outcome |
| --- | --- |
| Equal SDK pin, valid binding | Empty selection; still validates every binding |
| Changed SDK, unchanged ELF | Direct consumer selected; ELF equality cannot hide input change |
| Unrelated package and world variations | Only reverse closure selected, regardless of explicit-root membership |
| Chain, diamond, cycle, direct plus transitive path | Hand-written expected sets; no duplicate, omission or nontermination |
| Missing/stale/malformed binding, equal and changed candidates | Exact rejection, empty stdout; no inferred binding or partial plan |
| Receipt/artifact substitution or unsupported type | Exact rejection even if binding text alone is well-formed |
| Bad record/profile pin, pending state, invalid graph, v1 | Reject before emitting selection; no migration or repair |
| Each bound at limit and over limit | Complete success at supported limit; explicit failure above it |
| Hash tool fails with plausible output; scratch/write failure | Nonzero status; no accepted report from unverified data |
| Input changes during validation; failed stdout; interruption | Detect injected drift; report delivery failure; owned cleanup only |
| Every success and rejection | Before/after root bytes, entry types, modes and outside sentinels identical |

The [existing witness](evidence/sdk-static-package-2026-09-07/README.md) establishes
only the direct record/input observation. The focused fixture is `python3 tests/sdk-rebuild-plan.py`; it retains commands,
statuses and exact source identities under work/sdk-plan-*. Run
`python3 tests/check-development.py --lint mk/sdk-rebuild-plan.sh tests/check-fixtures.sh`
and `sh tests/check.sh` for changes to this helper. The original
[design checks](evidence/sdk-rebuild-design-2026-09-07/README.md) are historical
documentation evidence, not runtime validation. Runtime results and remaining
limits are recorded in the [implementation evidence](evidence/sdk-rebuild-plan-2026-09-07/README.md):
46 focused controls and the full suite pass. Exact positive maxima for every
metadata bound and hostile concurrency remain unproven.

Pinned Foundations I-01/I-02/I-03/I-05/I-06 govern contract, inert metadata, errors,
bounds and revalidation; I-08 preserves package/service authority. These are scoped
local implementation applications, not full runtime conformance or a new shared standard.
Owner review, complete static-input policy and native SDK-08 acceptance remain
separate. See [standards adoption](STANDARDS.md); no release pin changes follow.
