# Serial boot composition intake — 2026-10-03

Local BG-067 review supporting decision0181 and docs/SERIAL-BOOT-COMPOSITION.md.
No runtime or sibling change, new native execution, release-pin update or owner
approval is claimed. The preserved producer review is source/design evidence,
not a delivered lifecycle implementation. Source snapshots are reference inputs,
not build/runtime dependencies.

`producer/` preserves Aether's sealed serial-boot-contract packet verbatim.
`intake.json` records its manifest hash,21 verified members,12 source-current
comparisons and additional local/userland source origins, digests and lengths.
`current/` retains the nine enforcement/owner/build/userland inputs compared;
`local/` retains our current ABI22 owner/table/lock; `userland/` retains the runtime
experiment and independent serial acceptance references. Existing producer logs
report their historical checks only; this task did not rerun them.

The initial capture verified all producer packet bytes then rejected changed
native_launch.zig. `attempts/` retains that script and failure explanation. The
second capture distinguishes current changes instead of assuming a stale record
binds new sources. At capture, native_launch.zig/build.zig have unsealed009/selector
edits; native_c.zig and SESSION owner/helper sources still match the sealed review.
The producer's copied local disposition also predates the latest local edits.
Mutable current files are not promoted or qualified by this capture. Producer
source changes after capture do not rewrite these retained observations.

`capture.py` records the exact private capture operation; do not rerun it into
this retained root. `review.py` verifies captured producer membership/hashes and
captured current/additional-input correspondence entirely offline. It is an
integrity review, not a runtime or semantic acceptance oracle. `review.json` and
`validation/` retain this task's actual local results. `sha256.json` seals this
packet after validation, excluding only that manifest itself.

Selected direction: one sys-init-owned serial SESSION loop, bounded matched
userland runtime, and owner-only wait/halt enforced by Aether. Missing qualified
producer profile/runtime closure blocks wiring that path. ABI17/22/23 remain
separate, and the ABI22 developer recipe remains usable. Full protocol and
assembled-v1/independent review are still open.
