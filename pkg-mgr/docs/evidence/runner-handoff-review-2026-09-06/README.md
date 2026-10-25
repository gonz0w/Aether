# Runner handoff evidence review — 2026-09-06

Read-only package-side review of userland UL-058 bootstrap evidence and its pinned
UL-059 combined producer input. All 858 SHA256SUMS entries verify; all 293 source
archive members match the reviewed producer report. Ten native artifacts, nine
recorded ISO digests and five changed requester/client ELFs also verify. review.json
retains exact identities and the reviewed input files. Selected owner reports are
copied unchanged; no evidence command is executed and no owner source is edited.

The bootstrap fix has 22 UBSan host scenarios and two mutation rejections; the
original adapter had 13 failures. Nine native regressions pass on the finite legacy
runner, not the public aether-run consumer. Native injected bootstrap/reply controls,
remaining CB groups, public carrier/parser and combined consumer remain open. ASan
adapter and empty-main timeouts are explicitly incomplete; no ASan pass is inferred.

The existing package harness does not accept the owner's native-command-userland.v1
schema. Its old file-I/O profile is not an alias for the command tier. No guessed
case names, wire fields or acceptance selector is added. The owning command
consumption reference now supersedes stale UL-057-pending prose and defines the
next consumer receipt requirements. Aether's combined mechanism is available;
the next work is in the userland consumer, not a new blanket kernel API request.

This review does not qualify native package-manager execution, a package-rebuilt
command image, storage/persistence, service activation or publication. Cam's actual
reviews remain pending. Documentation-only validation uses development, standards,
source-assembly and whitespace checks; unrelated host/native execution is not rerun.
The frozen host-tested archive remains unchanged development evidence.
