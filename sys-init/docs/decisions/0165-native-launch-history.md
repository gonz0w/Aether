# 0165 — Actual native launch-to-history composition

BG-058, 2026-09-07. Implement decision 0164's first consuming witness using the
existing Driver reserve/channel/launch return path and original History storage.
No manually installed Applied Binding, synthetic successful return or sample_setup
may supply the positive path. Preserve the fixed token/owner profile distinction;
this remains synthetic issuance, not a native journal implementation.

Require received-but-unapplied launch to be ineligible, applied writer transfer,
retained reader/worker and generation, exact owner/token/worker matching, real
terminal O1/S/O2 capture and replay without further reads or launches. Explicit
fixture disposal must retain source history and consumed issuance. Positive 100/3;
controls skip applied-launch qualification (1071/0), retain transferred writer
(1072/0), forget received reader (1073/0), or skip full token match (1074/0).
All controls must fail the named semantic oracle, not a tool/size/boot failure.

Keep the 8192-byte ABI-15 image profile, pinned producer/worker, old native oracles,
ABI-6 byte compatibility and release pins. Run all 190 native cases and local gates;
retain build failures and exact source/artifact identities. No syscall, unsafe
site, public API, dependency, history reset or native retirement is added.
Foundations O-01/03/04, I-01/03–06 and E-01–08 apply; existing internal output
exceptions and smoke markers remain. Catalog acceptance still needs BG-056's
complete producer source closure; do not extend historical exceptions.

Preflight: an initial command-selection helper stopped before compiling (it selected
a non-build command); the corrected helper compiled all five probes. Initial source
layouts changed 64 legacy image byte sequences. Compile-time exclusions alone did
not restore them; retaining original source locations restored all 151 ABI-6 images.
The control additions deliberately share existing lines to preserve those locations.
Three source/build comparison snapshots are retained. The initial native run was
interrupted to add an exact 100/3 runner check, and the next was interrupted during
compatibility repair. Neither is a passing acceptance run. The first local check
rejected an invalid inventory layer label; it was corrected from native to target.

## Validation and handoff

Decision 0165 passes all 190 fresh Aether native cases. The new positive uses
actual Driver reservation, channel acquisition and received/applied launch before
moving the same records into History. Real terminal O1/S/O2 is retained; replay
performs no new reads or launch. Explicit fixture disposal preserves history and
consumed issuance. Four controls reject exactly at 1071/0, 1072/0, 1073/0 and
1074/0; the positive completes at 100/3.

All 185 previous ABI-15 images and 151 ABI-6 rebuilds remain byte-identical. All ten
local gates pass in `run-ge4pi5zf`, including 287 model tests; five focused runner
checks pass. Maximum native image is 7592/8192 bytes. Evidence is retained in
`docs/evidence/native-launch-history-2026-09-07/`, including interrupted runs,
preflight layouts, legacy byte differences and the corrected inventory check.

Fixed issuance remains synthetic; no native journal receipt, Cleaned admission or
retirement is implemented by this witness. Producer/worker and shared release pins
are unchanged. The catalog remains at 50 bundles/3019 historical outcomes pending
complete producer source closure under BG-056; no historical exception is extended.

Next BG-057: define and implement bounded native cut/effect ownership against the
qualified native launch/history path. BG-058 retains per-attempt cleanup/reclaim
provenance, BG-060 sustained reuse and BG-033 recovery. No new kernel prerequisite
was required for this one-attempt composition.

Technical review: existing ownership/return operations feed original history without manually creating Applied bindings. Controls are compile-time-only and preserve old source locations to retain embedded panic metadata. No new unsafe site, syscall, dependency or public API exists. The retained Sample clone is an oracle snapshot, not expanded production history. Documentation impact: native coverage, boundary/source digests, quality inventory and BG-057/BG-058 handoffs. No independent sign-off is claimed.
