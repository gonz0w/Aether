# ABI24 producer intake — 2026-10-03

BG-067 / decision0182. This review closes the stale missing-kernel-mechanism
status; matching userland wait-aware runtime and actual sys-init composition
remain open. Zero new native executions, runtime edits, sibling edits, released
pin changes or independent owner approval are claimed.

`capture.py` verifies three sealed Aether packets:91 lifecycle,112 session-owner
and78 endpoint-wait members. Every outer file, including each artifact archive,
was streamed/hash-checked before retention. The three large artifacts.tar.gz
files are intentionally omitted locally; their exact origin/digest/length and
omission are recorded in intake.json. Their internal members were not independently
replayed or audited here. All other278 producer members, three original manifests
and three current contract/runtime references are retained verbatim. Third-party
notices/source snapshots retain their original terms.

`review.py` uses only local captured bytes. It checks retained subset membership,
manifests, member hashes/lengths and the selected final receipt statuses. Names
are not outcomes: session-owner positive/positive-final are incomplete attempts;
short-session/wide-output are the actual accepted owner workloads. The withheld-input
client-limit case is an expected failure-limit witness, not healthy shell idle.
Channel-wait qualified is the final seven-generation producer probe, not dash.

Recorded results:009/ABI24 lifecycle idle3016/3007 with six reclaims; short/wide
shell workloads588/891 ticks, ten reclaims each; polling client limit1241 ticks;
endpoint probe3033/3023 idle with seven reclaims and retained12 trace corruptions.
These are producer results, not rerun sys-init acceptance. Existing wrong-profile,
authority/cleanup controls and legacy runs keep their producer scope. Inspected
session owner15184/24576 bytes and estimated3864/4088 stack leave a narrow stack
margin; any composed sys-init owner requires its own linked inspection.

The new selected profile retains finite SESSION identities/quotas. Owner wait/halt
and endpoint readiness wait do not confer child factory/UART authority. A readiness
hint requires another actual transfer, preserving partial offsets; EINTR does not
inject a signal handler. The current captured userland runtime remains008/ABI23.
No receipt claims that this polling client now uses009/ABI24 waiting.

Implementation map for the future consumer comes from the sealed owner source
archive: Session::pump handles transport/children/pipe retirement; run_lifecycle
owns observe-before-drain/park and parent settlement; _start checks profile/grants,
selects the session and closes UART before halt. The sys-init-owned policy/entry
must compose that dispatch explicitly. Copying/renaming the fixture or replacing
the ABI22 fixed command table does not supply that integration. The exact source
archive is retained; it is a reference, not a new build dependency.

`review.json` records offline integrity/status correspondence, and validation/
retains full local checks. sources/ binds changed guidance and process records.
sha256.json seals this packet after validation. Do not rerun capture into this root.
