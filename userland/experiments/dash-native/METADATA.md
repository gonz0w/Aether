# UL-007 launcher metadata consumer acceptance

Consumer review, 2026-09-08. The captured Aether documentation-only proposal is
AECAT002: separately selected 160-byte bootstrap with explicit real/effective
UID/GID, developer-only source kind, zero flags and zero reserved bytes. Exact
layout and owner contract remain in the [captured producer input](../../docs/evidence/dash-metadata-review-2026-09-08/producer-inputs/docs/NATIVE-SHELL-STARTUP.md).
This checklist maps consumer expectations to that proposal; it does not create a
shared ABI, grant owner approval or implement a second decoder.

The [review evidence](../../docs/evidence/dash-metadata-review-2026-09-08/README.md)
verifies all 12 archived inputs and the relevant unchanged upstream dash source.
The completed metadata delivery now has [local bounded evidence](../../docs/evidence/dash-metadata-consumer-2026-09-08/README.md).
The table distinguishes exercised cases from partial coverage; full metadata
contract and M3 acceptance are not inferred. Future intake still requires a matching
sender/decoder/getter/source/SDK/native-receipt delivery. Preserve
legacy AECAT001, the independently qualified parent query and existing workloads.

## Required metadata qualification

Run in the existing command suite with matched artifacts and independent exact
terminal/status/reclaim observations. Case suffixes below are local consumer test
identities under UL-007, not new shared requirements or duplicate backlog stories.
Producer fixture labels, exact numeric failure stages and resource bounds must
be bound at delivery; generic failure or timeout cannot satisfy a case.

| Case | Required observation | Native status |
| --- | --- | --- |
| UL007-META-01: distinct tuple | All four getters match separately supplied real/effective UID/GID; no role/PID-derived constants or field aliasing. | bounded evidence |
| UL007-META-02: reuse | Different valid tuples across fresh generations; each getter matches the current record, with native cleanup between generations. | bounded evidence |
| UL007-META-03: before admission | Each getter returns its all-ones sentinel and EAGAIN before readiness; every descriptor remains unavailable. Check errno per call. | bounded evidence |
| UL007-META-04: late invalid metadata | Source kind, flags, reserved bytes and each sentinel ID reject without publishing any getter or descriptor, including otherwise-valid preceding fields. | bounded evidence |
| UL007-META-05: descriptor failure | Existing malformed descriptor/rights and stale-generation controls still reject the whole record, including valid metadata. | bounded evidence |
| UL007-META-06: truncation | Header/body/metadata truncation rejects with bounded transport completion and owner teardown; no partial state or live peer left waiting. | bounded evidence |
| UL007-META-07: version directions | V1 sender/V2 receiver and V2 sender/V1 receiver reject after inspecting the header; account for unread bytes and peer closure. No downgrade or body-length deadlock. | bounded evidence |
| UL007-META-08: skipped publication | Mutation that omits metadata publication fails an exact semantic oracle even if ordinary copy/output still succeeds. | bounded evidence |
| UL007-META-09: zero identity | Effective UID zero retains denied read-only input writes and foreign native capability operations. The same denial boundary applies to nonzero metadata. | bounded evidence |
| UL007-META-10: actual init | Unchanged init/initvar with controlled empty environment produces PS1 `# ` for effective UID zero and `$ ` for nonzero effective UID; real UID must not substitute for effective UID. PPID remains correct. | bounded evidence |
| UL007-META-11: public/raw boundary | Public getters expose validated informational metadata; raw kernel UID/GID calls remain explicitly unsupported. No raw/public equality claim. | bounded evidence |
| UL007-META-12: failure readiness | Malformed public-signal bootstrap checks readiness through descriptors and metadata getters. Own-domain raw signal state remains a separate contract. Preserve legacy profile checks. | bounded evidence |

Accepted failure cases require their own owner cleanup oracle; do not relabel
zero-reclaim semantic mutants as recovery. Outer harness/emulator cleanup remains
a separate required observation. The producer's selected native controls and full
affected regressions must be captured; this review adds no new startup program.

## Prompt and environment scope

Pinned dash `var.c` initializes PS1 to `$ ` and switches it to `# ` when geteuid
returns zero. Environment import follows initvar, so an inherited PS1 can replace
that value. The initializer test must use the documented empty environment and
assert actual lookupvar output. A root-style prompt is not authenticated identity,
login, native authority or TTY acceptance. UL-010's authenticated-session work stays
separate. PWD/getcwd remains a known independent gap, not metadata acceptance.

## Full-main configuration gate

Pinned `main.c` surrounds the UID/GID equality condition before interactive ENV
loading with `#ifndef linux`. The retained reference wrapper selects
x86_64-linux-musl; its compiler defines linux. The exact imported main.o has no
undefined getuid/geteuid/getgid/getegid references. Thus this particular source
condition is absent from the current object; linking it with native getters cannot
restore the omitted code. This finding does not assert that every possible ENV
protection is absent or that a shipped native shell has a demonstrated vulnerability.
Native full main has not been qualified.

Before full-main/interactive ENV acceptance, select and review the native build
configuration and startup security behavior, including any secure-execution inputs
and environment filtering relied on by that configuration. Exercise equal UID/GID,
unequal UID and unequal GID tuples against an observable ENV script, plus relevant
privileged-mode behavior. Keep expected policy distinct from informational metadata
and existing native capability enforcement. These are later actual-main tests,
not prerequisites to reproducing the bounded initvar metadata witness.

This gives UL-081 a concrete configuration concern without a broad macro toggle,
upstream rewrite or new framework. Retain the current Linux reference objects and
evidence while selecting a separately pinned native configuration. Actual main,
external command/failed exec/wait and pipeline/EOF cleanup remain UL-007; full M3,
source trust and independent technical/reader review remain open.


## Historical qualification limits — 2026-09-08

The [case mapping](../../docs/evidence/dash-metadata-consumer-2026-09-08/coverage.json)
binds the309-case consumer run to these rows. Seven have bounded native evidence;
five remain partial. Complete independent per-getter errno checks (03), V2
malformed-descriptor composition (05), additional truncation boundaries (06),
queued mismatched-body teardown (07), and the other three raw getter calls (11)
before claiming the complete checklist. These are missing observations, not
runtime defects established by source inspection. Retain existing passing oracles;
no second decoder or unrelated utility matrix is required.


The separate [initial directory fixture](../../docs/evidence/dash-cwd-consumer-2026-09-09/README.md)
is locally reproduced as of2026-09-09: generated init resolves /work without its
former warning. Its directory matrix is incomplete and does not close these five
metadata rows or the full-main configuration gate above.


## Actual-main and metadata intake — 2026-09-09

The [369-case consumer reproduction](../../docs/evidence/dash-file-consumer-2026-09-09/README.md)
provides bounded evidence for the five formerly partial observations. The
[updated mapping](../../docs/evidence/dash-file-consumer-2026-09-09/metadata-coverage.json)
and18 exact final serial checks record per-getter errno/mutation controls, V2 bad
descriptor composition, selected EOF offsets0/16/48/144/159, coordinated V1/V2
mismatches leaving15 unread bytes, and all four raw getters. All12 checklist rows
now have bounded evidence; exhaustive framing/fuzzing, independent sign-off and
M3 remain separate. Historical seven/five counts above describe the earlier run.

Actual dash main and a basename script now execute with a separately pinned
AETHER_NATIVE_ENV_GUARD-enabled main object; the original Linux-reference main.o
is preserved. This addresses object selection, not the interactive ENV execution
matrix. Equal/mismatched identity, noninteractive/absent/empty ENV, omitted-guard
and unsupported -p controls remain open. Full-main NOT RUN statements above are
historical for the newly exercised no-ENV command/script scope only.


## Actual ENV execution checkpoint — 2026-09-10

[Independent 431-case qualification](../../docs/evidence/dash-helper-consumer-2026-09-10/README.md)
now covers equal UID/GID ENV loading, mismatch/noninteractive/absent/empty suppression,
old-main omitted-guard controls and explicit unsupported -p behavior. The separately
pinned enabled main executes; original Linux objects remain unchanged. This closes
the listed bounded ENV matrix gap, not authentication, set-ID, TTY, full shell
configuration or POSIX conformance. Earlier pending execution notes are historical.
