# UL-059 producer return candidate — 2026-09-07

This is a bounded source/evidence handoff for userland's independent review, pin
selection and rebuild. It is not a published standard, accepted consumer interface,
UL-059/067 completion or R1 release. Existing standards and consumer pins stay intact;
no sibling repository was modified and no message was sent on the user's behalf.

The [RL audit](RL-AUDIT.md) maps RL-01–12 to producer witnesses, four added controls
and remaining consumer/coverage limits. [Profile selection](PROFILES.md) identifies
source owners, cfg/defines, wire profiles and four-versus-six reclaim oracles.
[Contract](contract.md) records the requirement and forbidden outcomes before code.
The exact userland request documents remain inert inputs under review-inputs/.

## What to give the consumer

- `bundle.json`: archive/manifest SHA-256 values, sizes and candidate identity.
- `sources.tar.gz` and `source-manifest.json`: complete active regular-file source
  tree, including kernel/user/scripts/tests, boot/build configuration, planning,
  active docs, offline standards pins and reviewed process inputs. No git metadata,
  JJ state, caches, .deps, temporary files, output trees or docs/archive history.
- `evidence.tar.gz` and `evidence-members.json`: current receipts, binaries/native
  envelopes, generated text/carriers, logs and source snapshots; historical review
  records and every retained failed-attempt archive from the local-outcome program.
- `pack-verification.json`: independent extraction/member hash results and explicit
  source exclusions. `history-index.json` names omitted superseded successful-run
  archives, with hashes; their originals remain preserved in this repository.

Verify hashes against bundle.json before unpacking into a new private directory.
The source archive contains repository-relative regular files; the evidence archive
uses docs/evidence/... paths. Extracting both into the same private root restores
current evidence links. Historical metadata can refer to superseded success archives
explicitly omitted by history-index.json. No failed-attempt archive is omitted.
Hashes establish identity, not signer authentication or consumer approval.

The source archive deliberately excludes external pinned dependency caches and the
userland SDK. Reproduction requires independently provisioned matching tools/.deps
and the consumer's verified SDK closure; this is not a self-contained offline SDK
or a release image. Original BSD-2-Clause terms and third-party notices are preserved.
The recorded producer SDK is native-c-5olokhku; do not infer equivalence with a
consumer SDK solely from shared source hashes.

## Reproduction and acceptance boundary

From the extracted source root run the documented prerequisite setup, then
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` and
`python3 scripts/launch_smoke.py --command-runner --libc-build SDK --tools-lock LOCK`.
The executed producer uses `/Users/cam/DEV/Aether-userland/build/native-c-5olokhku`
and `/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same SDK/lock with --connections and --inherited-launch for compatibility.
Exact executed tool hashes, flags and generated-input identities are in receipts.

Userland must review this exact contract, choose an explicit new pin, build its own
clients, adapt role validation and wire its actual parser/frontend to native I/O,
then independently run applicable RL and existing child/legacy cases. Producer
fixtures deliberately do not duplicate command-line policy. Unknown admission or
collection cannot be treated as no admission, no child or successful reclamation.
General unknown-result recovery, exhaustive carrier truncation/fuzz, independent
reader review, extended testing and assembled shell/package/filesystem acceptance
remain open. No green inventory check waives those gates.

## Qualified inputs

All 140 command cases pass on this turn's first attempt, including the four audit
gap controls. Six connections and nine inherited-launch cases pass. All 98 Python
tests, Zig tests, offline pin/workflow and scoped formatting checks pass. Every
runtime source hash matches the three final receipts; kernel/build and SDK/libc/
tool-lock identities match the preceding qualification. The largest successful-
child owner remains 7,824/8,192 bytes. Exact run boundaries are retained; per-case
timestamps and independent/extended-stage evidence remain explicit limitations.

Packaging is a source-identity/extraction check, not a second independent build.
The inert `packaging.py.txt` records the one-off assembly recipe. Sources exclude
this evidence directory, and evidence-members.json separately binds evidence
archive members; bundle.json binds both archives and their verification records.
