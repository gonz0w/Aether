
### Approved separate name-profile implementation — 2026-10-20

The maintainer approved the preceding255/component510/rename profile. Implement
private `fs_names`, requiring the existing activation/runtime/bulk/wait/mixed
selection, with AFSRPC05 and `aether_fs_names_run` (same72-byte result/nine arguments).
Header words0..5 retain opcode/epoch/token/rights/length meanings. Words6..7 are
zero for named requests; word5 packs low32 source/high32 destination only for
rename. Each length1..255, combined<=510; non-rename has no second length. Receive
complete padded64-byte frames into the existing4096 scratch before dispatch.
Structural header/body errors consume/stop; complete lexical/policy denials may
reply and continue. Old versions and stale framing cannot resynchronize tails.
Unselected code, candidate bytes, kernel/provider and all other limits stay fixed.

Extend the existing owner checker and native driver explicitly, no new broker or
kernel operation. Host actual-entry tests cover current21 cases under selected
framing plus length/name/rename/partial/padding/epoch/rights/last-byte distinctions,
no-effect/retirement/reply-loss controls and compiling omissions. Check strict
Rust/Clippy/format/typed C ABI/object and old non-bitcode object compatibility;
never rewrite an old seal. A fresh matched seal/intake and actual controller fit
precede native qualification. Native names use64-byte digest components differing
only near the end. Replace the private controller's five recoverable preflight
checks with complete lexical/stale-token denials at the same count; malformed
version/epoch framing closes in AF05 and is covered in actual-entry host controls.
All9/96 transaction/request, full independent recovery, authority and other
verification checks remain. Stop any fit/time/failure for triage without expansion.
