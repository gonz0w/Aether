# 0199: Consume descriptor session and file-backed redirection

2026-10-22 / BG-067. Select userland41-member redirect candidate
1f808da2135af11be7a8225975a645a15a9b02d4ce84c3991ebea6d728901140,
its exact session36/predecessor dependencies and process15/service77 baseline.
Verify complete manifests before consumption; preserve older owners/pins/evidence.

Requirement: use the actual one-map session and source-backed FILE redirection
against unchanged sys-init Peer/handler/process/AF07 service over live host pipes,
with synthetic storage and separately owned actual stream pipes. Verify file
shared offsets after redirecting onto an occupied pipe target, actual old-target
EOF, nondestructive full/omit-cloexec snapshots, one-time startup and cached terminal
finish/raw closes. Known target refusal must preserve the map and close the
confirmed unpublished duplicate. Lost duplicate reply, uncertain target closure
with/no physical effect and lost cleanup reply must preserve the appropriate
receipt, retire without retry/publication and leave actual owner cleanup separate.
Retain independent file source counters and actual owned process/stream cleanup.

The simpler alternative is trusting producer tests or manually composing another
session/rollback ledger. Producer tests do not exercise our exchange wrapper;
choose the delivered one-map session/receipts and a small host consumer. Reuse
existing server App/fixture/driver and host stream callbacks, without runtime
changes, new protocol, second owner/ledger or generic machinery. No obsolete
accepted path is removed; existing experimental paths retain their exact scope.

Validate focused live cases and three compiling assertion-specific omissions,
strict C17/UBSan/format and Rust2024/default Clippy/rustfmt. Pin source/tools/host
libraries, discovered headers/resource headers and UBSan before actual build;
recheck afterwards. Compile60s/4MiB and paired-session30s/owned-group cleanup bounds.
Run full offline development checks. Native shell/startup/authenticated adapters,
copy/immutable exec/failed-exec guarantees and complete resource fit remain missing.
This does not claim atomic POSIX dup2, native settlement or native execution. No
sibling writes/messages, new guest, quota expansion, shared ABI or released pin.

## Result

[Evidence](../evidence/session-redirection-consumption-2026-10-22/README.md)
records14 selected closures/354 members,107 host C inputs/headers and38 Rust
compiler/host libraries. Six live positive/known-rollback/lost-dup/lost-cleanup/
unknown-target with/no physical close cases pass. Three compiling cleanup/
publication/unresolved omissions fail exact C assertions. All owned processes
stop; normal server source threads join. Raw source counters, actual stream
cleanup and cached receipt outcomes are independently checked. Strict C17/UBSan/
format and Rust/Clippy/format pass; selected inputs and tools remain unchanged.
No runtime source, native guest or old packet changes. Update the existing API,
handoff/planning and coverage surface; full native integration remains gated on
selected linked shell/startup/authenticated adapters/copy/exec/placement.
