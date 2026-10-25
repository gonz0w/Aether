# 0200: Prepare the descriptor startup producer

2026-10-22 / BG-067. Select userland56-member startup candidate
709a2c0f33b3cbf8dbecc3143d2976d5dd9093120cb4460eb41f697805147094
and its complete exact dependencies. Its AEFDB001 envelope is proposed, not the
selected shell ABI. Implement a separate allocation-free no_std producer using
our unchanged ABI29 identity encoder, explicit canonical bindings/source records
and retained pipe histories. Validate all shape/correspondence/identity fields
before changing caller-owned304 output bytes. Do not invent native grants.

Requirement: fixed version1/304 envelope, genuine boot parent7, same138 supported
shell/child identities, nonzero opaque file generation,16 kind-aware entries,
seven unique source records with exact rights/bounds/generation correspondence,
no orphan/missing sources, retained0..9 histories even when endpoints absent and
role-specific factory. Trusted caller owns actual admitted instance/channel/
source authority and single greeting delivery; packet creation confers none.
No I/O or send retry belongs in this pure encoder.

The simpler alternative is concatenating unvalidated byte slices at launch, or
waiting for the complete shell. The new concrete producer contract permits a
small checked encoder now; choose existing identity logic and explicit arrays,
without a second context/FD ledger, decoder framework, live owner change or
unreviewed native ABI. No obsolete accepted path is removed.

Validate Rust host identity/shape/output-preservation cases and three strictly
compiling omissions, then deliver actual Rust-generated frames to the exact C
startup/context/native consumer with injected native observations/transfers. Check
short reads/EAGAIN, single consumption/readmission, publication, scratch clearing,
independent raw closes, corrupt frames and EOF. Host injection is not native
execution/authentication. Build generic no_std target library only; no executable
or full code/stack/heap/context/workspace fit claim. Full offline checks required.
Keep input/tool/header/runtime closure, commands/results and owned bounded outputs.
No sibling edits/messages, guests, quota/default/released-pin changes or old
source/evidence rewrites. Selected shell/TLS/copy/exec/child rebind and full native
dispatcher/readiness/shutdown/fit still require matching owner inputs and witnesses.

## Result

[Evidence](../evidence/descriptor-startup-producer-2026-10-22/README.md) records
three passing Rust tests, three strictly compiling exact omissions,138 actual
producer-to-C-consumer admissions/1518 corruption rejections and generic native
library builds.16 source closures/494 members, tools/headers/runtime/libraries
recheck unchanged. The encoder uses caller-owned304 output and unchanged core;
no new unsafe/FFI/native boundary or accepted runtime changes. Current API, owner
handoff and existing startup coverage inventory are updated. Matching selected
native shell/child rebind/copy/exec/placement/full fit remain unresolved.
