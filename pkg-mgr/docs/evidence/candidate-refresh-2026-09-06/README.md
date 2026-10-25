# Refreshed public candidate qualification — 2026-09-06

Scope: local unpublished 187-file candidate incorporating the snapshot-hash,
preflight pipeline and record-comparison failure fixes. No release approval,
independent reviewer identity or supported security service is implied.

Archive SHA-256: `4530c8176b496003530a7ec8a306a5da6a0197550f7f7e0a32555d0163ba4843`.
Retained archive: `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-release.zj73uhbv/pkg-mgr-0.1.0-candidate.tar`.
The archive is 1,013,760 bytes; repeated assembly produces identical bytes and
host tar extraction matches the exact output manifest. input-files.json records
original source identities; documentation-edits.json records the public edition.
changes-since-previous.json identifies the 13 changed files against the earlier
public candidate: four runtime helpers, two tests and seven docs/inventory files.
No files were added or removed from the allowlist.

Selected checks: the extracted candidate's host preflight, full sixteen-fixture
suite, required manual rendering/lookup and bytecount lifecycle. In addition,
repeat-transactions.py invokes the extracted watchdog for two extra transaction
runs in fresh private roots with 300-second deadlines and completion markers.
The full suite has its own 600-second deadline. The full suite and first extra
run overlap in time; these observations are not comparative performance evidence.
Each repeated run must complete the producer/sort, comparison-error, killed
publication and ownership-conflict controls. No failed or incomplete run counts
as a successful repetition. Results/logs are retained separately.

The full suite passes all sixteen fixtures, three pinned standards gates,
whole-shell lint, watchdog controls, 71 source-record cases, eight hash-tool
faults, twelve producer/sort faults and six record-comparison error cases. Live
minisign fixture verification runs and passes. The required manual/bytecount
workflow also passes. Raw logs and host identities remain attached to this
archive; they do not retroactively qualify the earlier candidate.

All three transaction fixture runs pass, establishing only bounded repetition on
one host and these fixed inputs. They do not establish soak coverage, random fuzz,
real full-storage/power-loss recovery, hostile filesystem-race resistance,
concurrent writers or native package-manager execution. Each fixture uses its own
private roots; no live prefix is changed and no sources are downloaded.

Final post-test checks bind unchanged selected file bytes/modes and the retained
archive digest. Later project checkpoints are outside the tested archive. Pinned
tool acquisition/setup, broader boundary/failure qualification, independent
content/build/reader review, a monitored security contact and a publication
decision remain gates. Nothing has been tagged, signed or uploaded.
