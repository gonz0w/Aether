# Serialized inheritance v1 implementation review

Plan and simplicity/ownership/cleanup assessment recorded in docs/quality/change-review.md
before code. Actual implementing-agent review: additive API keeps old native-freeze
contract; exclusive Rust borrow spans callback/publication; shared child validation
preserves native syntax/epoch/capacity rules. Guard retires uncertainty on unknown,
unbound and unwind, never claims native termination or parent token thaw. Expected
identity is not a grant. One ledger, no new persistent fields/allocations/handles.
Owner must serialize streams/source access and authenticate native observations.

Initial minimum/current26-test/ten-control qualifications passed. Subsequent source
review found new result types needed re-export from the private processes module;
internal tests alone did not check external consumer usability. Added explicit
re-exports plus separate no_std external host/target consumer builds. Retain both
initial passes as partial coverage, then qualify final sources on both interpreters.
No compiler warning suppression or runtime weakening. No independent owner/reader
approval, wire allocation, native copy/rebind or full-link claim.

Source-only handoff: `build/service-deliveries/filesystem-serialized-copy-2026-10-22-v1`, 17 members; manifest SHA256
`01c185942e5449c9e2dadbe825f48642bcd81e4635ad63c19b0c75e1e7446d6a`. Contains predecessor process-source closure with exact
qualified maintained inputs, checker, new/local process contracts and dependency/
license receipts. The checker snapshot requires maintained repository layout and
pinned offline dependencies. This does not select an owner/native runtime.

All four exact owned attempts archived and streaming hash/size checked before
removal. Logical bytes removed 105,954,688; archive bytes
retained 25,568,128. Physical reclamation not measured.
Current Python/lzma is retention-only, separate from minimum-version qualification.
Final verification receipts accompany the seal. No sibling edits/messages, guest,
install, quota/default/pin change or monitoring. Independent owner/reader pending.
