# 0203: Enforce authoritative FILE snapshot comparison before copy

2026-10-22 / BG-071, BG-069/070. Local implementation and host qualification complete; native acceptance pending.

Consume additive file-view18 (manifest
bce3ead4e8a1583ef88e85eb494bb9f1d0d71167205e80b85c7e49cd121043a2),
retaining old serialized-copy17, frame69 and released pins. Under sole owner
admission, derive both complete masks from all sixteen tagged bindings, using
remote FILE selector bits rather than logical FD slots. Compare against the
current ProcessFiles file_view_v1 immediately before native copy. Malformed,
duplicate, missing, extra, wrong-flag, stale and retired views must not invoke
copy or mutate FILE state. Rejection closes the transaction without implicit
source cleanup, thaw or retry. Explicit owner reconciliation remains required.

This is safe-Rust local enforcement with actual AF07 libraries and synthetic
storage/native observations. Sixteen bounded binding iterations and four bytes
of temporary masks; no persistent ledger, allocation, new native call or shared
ABI. Actual stream/source/history comparison and native authentication are still
required; FILE validation alone must not claim the complete fork transaction.

Simpler alternative: compare caller-supplied masks in a callback. That leaves an
avoidable bypass at copy admission. Deriving directly from the complete binding
array at the gate is chosen. It removes the need for a second ledger or destructive
flag probes; it does not introduce a general validation framework.

Validation selected before implementation: actual-library success with logical FD
and remote selector differing, shared offsets and independent flags; complete-map
presence/flags/duplicate/malformed denials; stale/retired keys; no request/close or
copy callback on rejection; strictly compiling omission controls, host/native
no_std builds, pinned formatting/default Clippy and full local checks. Native
execution remains pending corrected userland ELF/TLS and complete owner wiring.

## Result and documentation impact

Nine actual-library gate tests pass, including all thirteen remote FILE flag bits
through reversed logical maps and inheritance; shared offsets and independent
flags retain exact values. Eight malformed/missing/extra/flag denial variants,
stale and retired keys cannot invoke copy or source effects and cannot retry.
Six strictly compiling omissions fail selected semantic assertions; real borrow
reentry is compiler-denied. Forty-three bounded final commands pass, including
pinned format/default Clippy and generic host/native no_std library builds.
Twenty-one recursive source deliveries/674 listed members verify before and after;
local compiled sources are pinned before and checked after. No new tool/dependency
license, unsafe/native boundary, shared protocol, heap or persistent ledger.

All ten aggregate development gates pass with unchanged captured sources. The
scoped quality record check also passes after final planning/reference updates.
[Retained evidence](../evidence/authoritative-fork-file-view-2026-10-22/README.md)
contains exact commands, source/artifact hashes and logs; prior successful source/
recipe snapshots are distinguished rather than overwritten. This packet is not a
native witness, full transaction acceptance or independent owner/reader approval.

BG-071/OQ-026 are locally resolved; BG-069/070 retain actual stream/source/rights/
history comparison, native holder/copy/refusal/greeting/ready/parent/terminal/
endpoint/readiness/shutdown composition and whole fit/fresh target acceptance.
Those local implementation steps remain actionable. Aether's actual loader
rejected exact stage81 for missing PT_TLS: corrected separately sealed userland
real-TLS relink plus loader acceptance is needed for native shell execution.
Preserve stage81 and old accepted owners/pins; no fake TLS or loader weakening.

Canonical fork guide and candidate README, current state/roadmap/priorities,
BG-069/070/071, open questions, standards/integration handoffs and quality inventory
now record the distinction between local work and final native inputs. No sibling
repository or immutable earlier evidence was modified; no guest was run.
