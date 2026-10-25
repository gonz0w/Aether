# Native evidence catalog and audit records

This reference describes [native-coverage.json](native-coverage.json) and
[scripts/check-native-evidence.py](../scripts/check-native-evidence.py). It records
the current historical audit contract, not a new native ABI or release format.
The [command manual](man/sys-init-check-native-evidence.1) covers CLI invocation;
[NATIVE-COVERAGE.md](NATIVE-COVERAGE.md) records the demonstrated target scope.
The audit reads retained artifacts; it never boots or executes them.
[Current evidence limits](EVIDENCE-LIMITS.md) consolidate verified scope, historical
omissions and the next operational priorities.

## Catalog and bundle fields

| Field | Meaning and current check |
| --- | --- |
| schema | Must equal `sys-init-native-coverage-v1` |
| scope | Nonempty bounded human description |
| bundles | Nonempty collection of bundle records; duplicate directory strings reject |
| bundle.directory | Relative, normalized POSIX path below the checkout; resolved escapes reject |
| bundle.manifest_sha256 | Expected SHA-256 of raw bundle `SHA256SUMS.json` bytes |
| bundle.schema | Expected result schema; `sys-init-native-init-v1` selects init auditing; the five supported I/O schemas below select the older I/O path |
| bundle.cases | Nonempty expected cases, with unique names; report names must match exactly |
| bundle.native_profile | Init only: `AENIN001` default or explicit `AENIN002`; other profiles reject |

The maintained I/O schema names are `sys-init-native-io-stop-v1`,
`sys-init-native-io-retained-v1`, `sys-init-native-readiness-v1`,
`sys-init-native-authority-v1` and `sys-init-native-peer-v1`. The catalog validator enforces this schema whitelist and exact fields before
bundle access. Init alone allows native_profile and case.first_image; first_image,
when present, must equal service-worker. Receipt/report validation remains separate.

The manifest is a nonempty JSON object with at most 10,000 normalized relative
artifact names mapped to lowercase 64-character SHA-256 strings. Names have the
same 4,096-character/control/path rules as catalog paths; the manifest may not
list itself. The complete map is validated before payload hashes are read.
Manifest JSON shares the catalog's 4 MiB, UTF-8, depth-32, duplicate-key and
non-finite rejection rules. One captured buffer supplies its pin hash and parser. Each listed file is hashed and compared. Every artifact required by an
audit must also be listed; merely existing on disk is insufficient. Manifest verification requires exactly the listed ordinary files plus
SHA256SUMS.json. Symlink/special entries reject; traversal allows at most 20,000
entries including directories and does not follow links. Empty directories are
allowed. Membership and manifest bytes are rechecked around payload hashing. A matching digest establishes bytes, not provenance,
freshness, reviewer authority or permission to execute.

## Expected cases and report selection

| Case field | I/O | Init |
| --- | --- | --- |
| name | Expected report `case` value | Expected report `name` value |
| smoke_exit | Expected integer smoke result | Not used |
| marker | Exact report marker and required serial line | Exact report marker; serial uses this unless expected_panic is truthy |
| assertion | Required serial line if truthy; maintained null means no extra assertion | Required serial line before the sole recognized outcome |
| expected_panic | Not used | Expected report value; a truthy value selects `AETHER PANIC: <value>` as serial outcome |
| context | Not used | Compared with the report's context; not independently derived from serial |
| first_image | Not used | `service-worker` selects retained service ELF; other/absent values select producer helper1 |

Both paths require matching report schema, result `pass`, sources_unchanged exactly
true, smp exactly false, and exact unique case membership. I/O additionally
requires native_memory exactly false. Init requires matching supported
native_profile; it does not independently check a native_memory field.

I/O commands are grouped by report case order: three per case with integer exits
`0, 0, smoke_exit`. Any command `outcome` field rejects, including timeout or
interruption. Case smoke_exit must be an integer (booleans reject), result must be
pass, and marker/exit must match the expected case. Init requires four leading
dependency/tool receipts plus three commands per case, all with integer exit zero
and no outcome field. Init case result, expected_panic, context and marker must
match. The audit does not independently authenticate command argv or rerun commands.

## Required identity chains

All paths below are relative to the selected retained bundle and must be listed
in its manifest. `results.json` is always required.

For I/O, the report pins `sdk-evidence.json` with sdk_receipt_sha256. Each case
pins `<name>-serial.log` and `clients/<name>/supervised.bin` via serial_sha256 and
envelope_sha256. `clients/<name>/build.json` must agree with report.native_sha256
and the envelope hash. This audit path does not structurally decode the older
supervised envelope or recursively validate all SDK receipt fields.

For init, report.summary_sha256 pins `producer/summary.json`; that summary pins
`producer/producer-sources.tar.gz` and `producer/init/results.json`. The producer
report must have status pass and profile `init` or `init-large` as appropriate,
with exactly one positive case pinning `producer/init/positive/native-c.bin`.
Its decoded first/second images must equal `producer/init/helper1.elf` and
`producer/init/helper2.elf`. The source archive is hashed, not extracted or run.

When any expected case selects service-worker, `worker/service-worker.elf` and
`worker/evidence.json` must match the consumer report's service_worker_sha256 and
service_worker_receipt_sha256. The worker receipt must say pass and repeat the
worker digest. Its optional inputs map, when present, is checked against listed
`worker/<name>` files; absence currently defaults to an empty map.

Each init case pins `cases/<name>/native-serial.log`, `native-c.bin` and
`supervisor.raw` with serial_sha256, envelope_sha256 and supervisor_sha256. The
consumer envelope must contain the producer entropy, selected first image,
producer second image and exact retained supervisor bytes.

## Envelope and serial rules

The init envelope has a 56-byte header: eight-byte profile magic; four
little-endian unsigned 32-bit words (first-image length, second-image length,
supervisor length, zero reserved word); then 32 bytes of entropy. Each image
length is 1–1,048,576 bytes. Supervisor length is 1–4,096 for AENIN001 or
1–8,192 for AENIN002. Total length must exactly match header plus payloads.
This is an offline structural/correspondence check, not native loader acceptance.

Init serial must contain exactly one recognized outcome: one of the ordinary or
LARGE PASS/CLOSED markers, or a line starting `AETHER PANIC:`. That outcome must
match the selected expected value, and the required assertion must occur earlier.
Other unrecognized log lines are permitted. I/O serial checks are weaker: required
marker membership, no I/O PASS line for a nonzero smoke result, positive completion
line `NATIVE supervisor result=100 reclaimed=2` for zero exit, and any requested
assertion. I/O does not impose the same unique-outcome/order rule as init.

## Result, lifetime and remaining work

Success stdout is JSON with schema `sys-init-native-evidence-audit-v1`, result
`pass`, catalog_sha256, bundles, recorded_cases, and native `not-run`. Each bundle
result has directory, cases, files and result pass. Counts describe audited
catalog entries, not current-source qualification or new target executions.
The checker does not write evidence, update pins or repair records.

Help/version exit zero; bad arguments exit 64. Caught ValueError, KeyError,
TypeError and OSError failures print `native evidence audit: ...` on stderr and
exit 1 without failure JSON. Diagnostics are not escaped; other exceptions can
bypass this path. Preserve exit status as well as output.

Catalog JSON is UTF-8 and at most 4 MiB/32 nesting levels. Duplicate keys and
non-finite constants reject. Exact top-level/bundle/case fields, scalar types,
normalized relative paths, lowercase 64-character digests and unique names are
validated before bundle reads. Case names are single path components. Text is
1–4,096 characters without ASCII controls or DEL; nullable init marker/context/
expected_panic and I/O assertion are allowed. Init assertion is required, and an
init case needs a marker or expected_panic. I/O smoke_exit is an integer 0–255,
excluding booleans. Bundles and cases per bundle allow 1–1,000 entries; total
cases are capped at 10,000. The catalog digest uses the bytes parsed.

Receipt/report JSON uses the same bounded strict UTF-8 parser and requires an
object root. Duplicate keys, depth above 32, non-finite literals and numeric
overflow to infinity reject. Finite numeric values are preserved; complete
per-schema field/type validation is still separate.
Digest reads stream in at most 64 KiB chunks, with a 64 MiB per-file limit.
Hashing requires ordinary files and rejects symlink components below the supplied
checkout root. Nonblocking/no-follow opens, descriptor identity and post-read
size/mtime checks apply, and descriptors close on failure. Empty files hash
normally. JSON/serial/envelope and helper-image content reads also require ordinary files,
with the same component/descriptor checks and a 4 MiB buffer limit. Serial text decoding uses the host default and universal newline conversion;
receipt JSON decodes UTF-8 from the verified captured bytes.
They reopen files, but each captured buffer is checked against the pinned
manifest before decoding or semantic parsing. Receipt-correspondence digest reads
must also match that manifest. This binds consumed bytes to the verified map,
without making the filesystem tree atomic or detecting every later change.

Catalog and manifest reads require ordinary files without symlink components
at/below the supplied root, using nonblocking/no-follow opens where available.
Descriptor type/device/inode are checked before reading and size/mtime after;
descriptors close on failure. At most 4 MiB plus one detection byte is read.
Each bundle is reverified after semantic checks. Before CLI success, every bundle
is verified again and catalog bytes must match the original capture. These are
sequential consistency checks, not an atomic filesystem view. The
standalone audit has no I/O deadline; aggregate timing is a separate boundary.

BG-056 follow-ups: SDK receipt recursion and additional correspondence, filesystem I/O
deadlines and independently reviewed acceptance of the remaining race limits. Preserve historical
bytes when adding checks. These are known gaps, not approved exceptions. Independent
review and current-input native acceptance remain separate.

[Existing native audit controls](../tests/test_harness_native_audit.py) cover
malformed case sets, command outcomes, serial semantics, envelope bounds and
repinned artifact mismatches. [Catalog controls](../tests/test_harness_native_catalog.py)
add top-level rejection before bundle access and required manifest membership.

Decision 0126 [catalog validation tests](../tests/test_harness_native_catalog_validation.py)
cover early rejection, current-catalog compatibility, JSON limits and parsed-byte
report identity. Decisions 0127–0131 add file policy and final checks;
same-byte reporting still does not establish an atomic filesystem snapshot.

Decision 0127 [metadata tests](../tests/test_harness_native_metadata.py) cover
FIFO/link rejection, malformed matching-pin manifests before payload access,
captured-byte parsing, oversized files and controlled replacement/growth. They
do not establish hostile-directory-race protection or filesystem I/O deadlines.

Decision 0128 [hashing tests](../tests/test_harness_native_hashing.py) verify raw
digest compatibility, chunk sizes, ordinary-file/size rejection, controlled
replacement/growth and descriptor cleanup on read errors. The limit-boundary test
lowers the constant for a small fixture. Later decisions add verified semantic
reads and final consistency; strict receipt schemas remain BG-056 work.

Decision 0129 [content tests](../tests/test_harness_native_content.py) verify text
compatibility, JSON/serial/envelope type/size rejection at semantic-read time and
read-error cleanup. Decision 0130 binds semantic content to the pinned manifest; decision 0132 adds
strict JSON parsing. Per-schema fields/types remain separate work.

Decision 0130 [verified-content tests](../tests/test_harness_native_verified_content.py)
cover late JSON/serial/envelope changes, verified capture use despite subsequent
file replacement, and receipt-digest consistency with the manifest.
Decision 0131 strengthens the capture-use control to require final rejection of
post-capture mutation. Strict receipt schemas remain BG-056 work.

Decision 0131 [consistency controls](../tests/test_harness_native_consistency.py)
cover extra/special files, post-hash membership changes, the entry budget and
changes to earlier bundles during later auditing. Updated metadata/catalog/content
controls reject late record changes before success. Changes restored between
comparisons or occurring after the last comparison can still escape detection.
Filesystem I/O deadlines, strict receipts and independent review remain open.

Decision 0132 [receipt JSON tests](../tests/test_harness_native_receipt_json.py)
exercise all five receipt-reading sites and duplicate/depth/root/encoding/number
controls. This enforces JSON syntax and object roots without claiming complete
receipt schema conformance or changing the retained receipt bytes.


## Consumer report fields — decision 0133

Consumer results.json is validated before linked receipt access. I/O reports require
schema, result, sources_unchanged, smp, native_memory, native_sha256,
sdk_receipt_sha256, cases and commands. Init reports replace the three I/O-specific
fields with native_profile and summary_sha256; paired service_worker_sha256 and
service_worker_receipt_sha256 are required for service-worker cases and otherwise
optional. Optional build_profile is retained-sampling-v1, suffixed -abi15 for
AENIN002. Unknown fields reject at report, case and command levels.

I/O cases require case, result, smoke_exit, marker, envelope_sha256, image_sha256
and serial_sha256. Init cases require name, result, context, expected_panic, marker,
envelope_sha256, iso_sha256, serial_sha256 and supervisor_sha256. Only init marker,
context and expected_panic permit null. Case names are normalized single path
components. All digests require 64 lowercase hexadecimal characters. Image/ISO
hashes are structurally checked; this adds no artifact-correspondence oracle.

Booleans must be actual booleans; smoke_exit is an integer 0–255 and command exit
an integer -255–255, excluding booleans. Commands have exactly argv and exit.
Reports contain 1–1,000 cases and 1–3,004 commands; each argv contains 1–1,000
strings. Text is 1–4,096 characters without ASCII controls/DEL; only argv elements
may be empty. Existing semantic checks still enforce report success, expected
case membership, command count/order and expected exits. These bounds describe
retained consumer reports, not a new shared ABI.

The report-field tests cover all 50 retained report variants, malformed fields,
bounds, worker-pin requirements and rejection before linked receipt parsing.
Producer summaries/reports and worker/build receipts remain separate schema work.


## Linked receipt fields — decision 0134

Every semantically consumed producer summary/report, service-worker receipt and
I/O supervisor build receipt gets field validation immediately after JSON parsing.
All objects require exact known fields. Digest maps contain 1–10,000 normalized
relative names with lowercase SHA-256 values. Commands contain 1–1,000 argv lists,
each with 1–1,000 strings; text uses the consumer 4,096-character/control limits.
Recorded paths, tool identities and commands are descriptive data, never executed.

Producer summaries require inputs, scope, source_archive_sha256 and suites.
Legacy summaries have no other fields; host summaries additionally require host
and tools. Normalized summaries instead require schema
sys-init-normalized-producer-v1, native_profile AENIN002, upstream_manifest_sha256
and upstream_producer_sha256. Suites require init and allow 1–64 named entries;
legacy/host suite records contain output, report_sha256 and integer cases 1–1,000.
Normalized suite records contain only report_sha256. Tools contain 1–64 named
records with path, resolved_path, sha256 and version.

Producer reports require cases, commands, libc_receipt_sha256, libc_sha256,
profile, sources, status, tools and tools_lock_sha256. Profile is init/init-large
and status is pass. Their 1–1,000 cases have unique single-component names, pass
status and envelope_sha256, iso_sha256 and serial_sha256. This validation does not
re-run producer suites or establish additional ISO/serial artifact correspondence.

Service-worker receipts require commands, inputs, inputs_unchanged, libc_sha256,
program_headers, result, schema, sdk_receipt_sha256, tools_lock_sha256, tools_used
and worker_sha256. Schema is sys-init-native-service-worker-v1, result is pass and
inputs_unchanged is exactly true. Inputs are nonempty; tools_used has 1–64 unique
names. The 1–64 program-header rows each have eight unsigned integers: the first
two fit 32 bits and the remaining six fit 64 bits. Booleans are not integers.
Header validation is structural, not a fresh ELF loader or correspondence check.

I/O supervisor build receipts require command, envelope_sha256, native_sha256,
supervisor_sha256 and variant. Command is an argv list, variant is bounded text
and all three hashes are digest strings. Existing producer/consumer identity
comparisons remain in force. SDK recursive schemas, unconsumed I/O worker reports
and additional artifact correspondence remain BG-056 work.


## Retained artifact links — decision 0135

I/O build supervisor_sha256 is compared with the verified retained
clients/<case>/supervisor.raw. Service-worker input maps must include
inputs/sdk-evidence.json, inputs/tools.lock.json and inputs/libc.a, matching their
sdk_receipt_sha256, tools_lock_sha256 and libc_sha256 fields respectively. Existing
input-map verification binds those links to retained files. All 22 supervisor
links and all three links in 18 worker receipts match the historical evidence.

None of the 2,997 init consumer ISO digests has a retained matching artifact;
those remain structurally checked claims. The first I/O bundle has no original
native envelope; four later bundles retain worker/native-c.bin. Historical gaps
are preserved, not silently filled from current builds. SDK recursive semantics
and further envelope correspondence remain separate BG-056 scope review.


## I/O embedded correspondence — decision 0136

The audit parses each AENFD001 envelope as an exact 48-byte header (8-byte magic,
two little-endian uint32 lengths, 32 entropy bytes), 1–1,048,576 native image bytes
and 1–4,096 supervisor bytes. Truncation, trailing data and invalid lengths reject.
It reconstructs AENATC01 + entropy + native image in memory, compares its SHA-256
with consumer native_sha256 and compares the embedded supervisor with verified
supervisor.raw. All 22 retained I/O cases match. Existing manifest/buffer checks
apply before decoding. Reconstructed bytes are not written or executed.

This also checks the first bundle's recorded native identity despite its missing
independent original file; it does not manufacture a new historical artifact.
Direct/derived SDK receipt semantics and unavailable ISO artifacts remain separate
limits. This is host correspondence evidence, not native loader conformance.


## SDK receipt fields — decision 0137

Fixed SDK read locations now use strict verified JSON parsing and field validation:
top-level I/O sdk-evidence.json and worker/inputs/sdk-evidence.json. Derived I/O
receipts follow the latter path once, compare sdk_receipt_sha256 and require the
direct format there. Service-worker SDK inputs also require direct format. No
receipt-provided output, command, artifact name or patch path is opened/executed.

Both formats require artifacts, envelope_sha256, probe_variant and scope. Direct
receipts additionally require checks, compiler_runtime, entropy, io_adapter_sha256,
libc_archive_sha256, libc_patches, native_entry, output, probe_sha256, script_sha256,
source_sha256 and tools_lock_sha256; probe_variant is io. Derived receipts instead
require commands, inputs, inputs_unchanged, program_headers, sdk_receipt_sha256 and
tools_used; variants are io-retained, io-readiness, io-authority or io-peer.
Inputs must include the matching SDK digest and inputs_unchanged must be true.
Unknown fields reject throughout these records.

Artifacts have unique names and SHA-256 values. Direct artifacts also require
unsigned 64-bit bytes, unsigned 32-bit static_syscall_instruction_sites and header
rows (eight integers: two uint32, six uint64). Patches require unique name, relative
path, before_sha256, after_sha256, reference_evidence_sha256, reference_patch_sha256,
old and new. Patch text allows 1–65,536 characters with tab/CR/LF; other ASCII
controls and DEL reject. Other text retains the 4,096-character single-line rule.

Artifacts, patches, checks, tools and header lists each contain 1–64 entries;
commands/argv and input maps retain their 1,000/10,000 limits. Booleans do not count
as integers. All 23 direct occurrences and four derived receipts pass. These are
structural checks; named checks, patch effects, instruction counts and ELF header
claims are not independently repeated or certified. Additional SDK semantic and
artifact correspondence remains BG-056 work, with missing artifacts explicitly
excluded. No shared ABI, release pin or historical receipt is changed.


## Derived SDK correspondence — decision 0138

For each of the four derived receipts, every input-map digest is compared with
its verified worker/<input-name> file. The artifact list must contain exactly one
startup entry, matching worker/worker.elf. The verified worker/native-c.bin digest
must equal both SDK envelope_sha256 and consumer native_sha256. Its AENATC01
layout requires 32 entropy bytes and 1–1,048,576 image bytes; the embedded image
must equal the verified worker ELF. All 904 input links and eight artifact links
match. All content uses existing bounded verified reads; nothing is executed.

The first direct receipt's sdk/startup/bad-dup artifacts are unavailable. Their
claims remain structural; no mapping or historical artifact is invented. Direct
SDK semantics, missing artifacts and further producer correspondence remain
BG-056 follow-ons alongside filesystem limits and independent review.


## Producer consistency — decision 0139

Legacy/host summary init-case counts must equal their producer report case count;
five normalized summaries legitimately omit counts. Producer libc_receipt_sha256,
libc_sha256 and tools_lock_sha256 must match consumed worker sdk_receipt_sha256,
libc_sha256 and tools_lock_sha256. Existing worker checks bind those values to
retained files. All 40 counts and 54 dependency links match; no extra reads occur.

The 27 producer bundles without workers lack matching standalone SDK/libc/tool
lock files. Among 395 producer cases, 45 positive envelopes are retained at their
expected paths; 350 other envelopes and all producer case serials/ISOs are absent
there. Existing positive envelope/helper checks do not audit the full suite.
The 8,307 summary input and 3,430 producer source path occurrences are not retained
as standalone producer files. Source-archive member checking requires a separately
bounded archive review; no extraction or inferred correspondence is added here.


## Source archive correspondence — decision 0140

The verified producer-sources.tar.gz buffer now expands in memory with a 32 MiB
ceiling (plus one sentinel byte to detect overflow), then uses the standard tar
reader without filesystem extraction. Only regular nonsparse members are allowed,
with normalized relative names, no duplicates, at most 10,000 members and 4 MiB
per file. Member hashes use 64 KiB reads. The complete archive name/digest map
must equal summary inputs. Historical PAX mtime records remain supported; tar
metadata and padding count toward the expansion ceiling. The ordinary verified
compressed read retains its existing 4 MiB bound. No member path is opened.

All 45 archives and 8,307 summary input entries match. Largest observed values:
401 members, 3,528,344 compressed bytes, 9,737,622 member-content bytes and
3,653,632 bytes/file. This verifies summary inputs, not full producer source maps:
3,420 producer source entries match, but ten .DS_Store references are absent in
five normalized archives (kernel/.DS_Store and kernel/arch/.DS_Store). Retained
receipts are unchanged. Source authenticity, patch/build provenance, missing
producer artifacts and independent review remain separate limits. Standard tar
parsing semantics apply; this is not a canonical tar-byte-format validator.


## Producer source-map checks — decision 0141

All producer source entries must match the archive-verified summary input map.
The checker permits only ten historical missing metadata entries: kernel/.DS_Store
and kernel/arch/.DS_Store in the five normalized bundles, restricted to the exact
manifest pins and recorded hashes in SOURCE_OMISSION_PINS/SOURCE_OMISSION_HASHES.
The normalized schema is also required. A changed pin, unknown missing name or
changed digest rejects; an entry present with a conflicting digest always rejects.
This verifies 3,420 available entries and preserves ten explicit unverified claims.
It does not assert complete producer source closure for those five bundles.
New/repinned evidence gets no inherited omission waiver. See STANDARDS.md.
