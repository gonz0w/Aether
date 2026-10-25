# ABI9 command producer intake — 2026-09-08

BG-067 producer input intake and fresh reference-image replay. See the
[adapter review](../../INIT-COMMAND-ADAPTER.md) for the actual ownership changes
still required. No native sys-init owner implementation or acceptance is claimed.

producer/ is the exact 38-file manifest-pinned packet, including its 196-source
and 218-artifact archives and earlier failures. intake.json records manifest/SDK
pins and verified archive membership; imported notices remain unchanged. The
contract is copied from the verified archive. No runtime/released pin is replaced.

All five supplied images freshly pass in local QEMU with the pinned executable
and existing matching boot dependencies. The driver verifies exact ISO hashes,
terminal lines and supervisor/reclaim results. Positive, empty and fault require
two generations/six reclaims. Wrong-role and skip-close require exact rejection
and zero reclaims; these are not recovered cleanup. replay.json and replay/ retain
commands, results and raw logs. ISOs are retained in the producer artifact archive.
No source rebuild or independent lifecycle implementation follows from replay.

Full local checks are recorded after validation. No sibling repository was changed.
sha256.json seals this intake bundle, excluding itself. Independent review,
paired-connection owner implementation, sustained boot and operator shutdown
remain open. The producer handoff availability blocker is resolved.

Final validation: all ten local gates pass in run-jtu44hvs with checked source
inputs unchanged. Packet hashes, new reference links, released locks and
`git diff --check` pass. Five fresh producer-image replays pass; no new failed
replay attempt occurred. Producer failed attempts remain retained unchanged.
