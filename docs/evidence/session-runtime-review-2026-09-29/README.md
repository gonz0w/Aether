# Bounded session runtime technical review — 2026-09-29

Requirement before changes: review the delivered private008 runtime candidate
against Aether's accepted ABI/grant/fixture contracts, verify sealed evidence and
perform a fresh isolated offline component rebuild. Foundations O-01–05 and
E-01/E-04/E-05/E-08 apply. Userland records the explicit maintainer ownership
assignment; Aether retains native enforcement and fixture ownership. This intake
does not write siblings or infer permission to do so.

Selection: complete extraction seal and candidate manifest verification; source
extraction comparison; bootstrap/state, application/authority and component gate
review; native receipt scope and independent comparison review; isolated rebuild
and whole-ELF equality; local host/pin/workflow/link checks. Native execution is
attributed to userland's fresh49 runs; no new runtime, ABI, grants, quotas or unsafe
boundaries are implemented here. Preserve all prior pins and sealed packets.

Forbidden outcomes: human reader approval, public SDK publication, full SSDK-01–06
or R1 acceptance from bounded fixtures, new authority from paths/metadata, or using
this008 candidate as SI-07's missing sustained transport/runner delivery.

Verified1391 extraction evidence members and571 self-contained candidate members.
review.json binds extraction/candidate seals and worker identities. A fresh isolated
local offline rebuild under zig-out/session-runtime-review-2026-09-29 matches both
native-tested whole ELFs; rebuild-results.json retains exact commands/environment,
tool digests and checked process cleanup. The small owned input/output tree is compacted into build-artifacts.tar.gz; every
file is hash/size verified by readback before removing only that temporary root.
No large native suite or duplicate historical archive was generated.
Selected consumer receipts, reviewed candidate sources/recipe and the two external
manifests are copied here. Those copied manifests describe complete external inputs;
this packet's own SHA256SUMS covers the selected copies and local review results.

[REVIEW.md](REVIEW.md) records source/authority/state/component findings and scoped
SSDK dispositions. Receipt checks verify49 executions, serial producer owner hashes,
304 current runtime sources and15 rejection controls. The initial receipt selection
and existing-output assertion failures are retained and corrected without any change
to native evidence. No newly identified kernel enforcement defect blocks the bounded
extraction. Independent human technical/reader findings and collective SSDK-01–06
consumer/owner disposition remain absent. SI-07 remains blocked on its distinct
sustained transport/bootstrap and rebuilt runner/bytecount. No sibling, release pin,
kernel source, resource bound or native authority changed.

Local host checks pass132 Python tests and configured Rust/Zig/offline pin checks.
Workflow, Foundations, simplicity snapshot, intake links/syntax and scoped whitespace
checks pass. checks.json records selection; retention.json binds the indexed artifact
archive containing complete local build commands, outputs and source inputs.
