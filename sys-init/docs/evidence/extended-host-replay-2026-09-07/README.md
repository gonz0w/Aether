# EHT-01 replay and platform handoff — 2026-09-07

Decision 0148 verifies the original campaign's first seed through the real CLI.
All 54 executions pass, with no skips; the entire worker record matches the
original seed, including exact order and plan/corpus/implementation identities.
The original 77-file evidence manifest verifies. This replay is separate from
the eight-seed campaign and does not count as another 432-case qualification.

`command.json`, `replay.stdout`, `replay.stderr` and `replay/` retain the actual
command, return status and raw results. `validation/` and `checks.log` retain all
ten passing gates with unchanged sources. `review.json` records preservation of
native audit output, 24 native inputs, catalog and all three release locks.

`environment-attempt.json` is explicitly a transcription of tool results, not
raw subprocess output. The existing Podman VM was stopped; startup reported
success but it was stopped again when checked after connection refusal. No
container/image verification or Linux test executed. No images were downloaded,
VM recreated or sibling repository modified. Cause was not diagnosed here.

A functioning additional host and an independent technical/reader reviewer are
required for broader qualification. The same agent's consistency review is not
independent sign-off. No hosted scheduling, release acceptance or new native
behavior is claimed. Preserve this attempt alongside the earlier Linux snapshot;
that snapshot does not qualify current source bytes.
