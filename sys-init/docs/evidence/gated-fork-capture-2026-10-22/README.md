# Gated fork capture and native owner placement — 2026-10-22

[Decision0205](../../decisions/0205-gated-fork-capture-and-placement.md),
[API](../../../prototypes/native-filesystem-session/FORK.md),
[focused unsent placement handoff](../../OWNER-PLACEMENT-HANDOFF.md).

Twenty actual-library/core/capture host tests pass (15 retained, five added),
including all304 truncated prefixes, malformed16-byte header/no body consumption,
body/identity/reserved corruption, zero/replayed/gapped/final sequences, seven-byte
short reads/EAGAIN waits, raw wait/count/EOF/budget failures and clear-on-return/
error/host-unwind. Receiving prevents copy after incomplete/failed/unwound capture;
Capturing permits it only after sequence validation. Source fixtures are synthetic
storage and scripted native channel observations. No native transport execution.

Thirty-three bounded final Rust commands pass: strict format/default Clippy,
host/native gate/owned-stream/unchanged endpoint/new transport libraries,20 tests,
and four compiling omissions (early copy while receiving, replay acceptance,
unsupported-header body consumption, missing unwind buffer clearing). Altered
trait-dependent consumers rebuild against the changed gate; only one semantic
assertion failure/exit101 counts, never compile/link failure. Two earlier passing
source/recipe snapshots are retained: initial-twenty-tests before redundant buffer
clearing removal/overcount coverage, before-helper-simplification before removing
an unnecessary immediate closure. No failed tool attempt occurred in this slice.
Historical artifact paths represent hashes, not retained binaries.

preparation.json records exact21 sealed source closures/674 members, pinned reused
unchanged dependency artifacts from0203, tools/host/native libraries and local
pre/post source/fixture identities. Accepted ABI24 pipe and AF07 endpoint/native
source stay unchanged. New native libraries contain the previously reviewed
endpoint assembly; no new unsafe/native boundary was introduced.

placement.json/target-layout.ll.txt compile actual concrete native Framed/Endpoints
x86_64 types: ProcessFiles2208, owned streams736, full gate2968, workspace4096,
Plan216 and transient fork buffers608 bytes. Actual current kernel maps owner
code RO/executable and one stack page at0x800000 with entry RSP0x801000-8; supervisor
memoryOperation rejects allocation, and owner linker disallows writable image data.
Gate+workspace7064 (Files+workspace6304) exceeds even the mapped4096 bytes, before
additional peer/call frames. This is a static resident-placement impossibility
under current contracts, not full owner code/stack/heap/peak-fit measurement.
Kernel source excerpts/whole-file pins and private layout probe command are retained.

BG-072 asks Aether for an opt-in8192-byte zeroed private RW/NX region from its
existing128-page owner partition. No general allocator, quota/stack/code expansion,
guessed capability, mutable code, second FS owner or profile/pin change is made.
Other producer FILE/stream/corrected-TLS inputs remain resolved; no new userland
request is assigned. Full native wiring/fit/witnesses wait for actual placement
contract, authority and matching producer evidence. This handoff is unsent.

runner.py.txt and placement-runner.py.txt are trusted inert reproduction recipes;
use fresh private output/evidence roots and pinned0203 dependency artifacts (or
rebuild them with the earlier exact recipe). Raw logs/inputs/artifact identities,
source selection and all attempts are retained; no SDK tree, guest, sibling edit/
message, release/default pin change or independent owner/reader sign-off.
Full development checks are recorded in full-check.json. Native panic-abort does
not guarantee buffer cleanup; a blocked kernel wait is not wall-clock bounded by
our poll counter. Actual native obligation reconciliation/watchdog stays required.
