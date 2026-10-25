# AF07-backed shared descriptions — 2026-10-21

UL-007/081/082. [Contract](../../proposals/FS-REMOTE-DESCRIPTORS.md),
[pre-code plan/review](review.md), dependency-pins.json and summary.json bind scope.
The shared algorithm now serves the dedicated Owner adapter and a new AF07 client
adapter. Remote owns a fresh authenticated client, constructs no Owner/SPA and
reuses unchanged sealed service wire. Added client abort records both local
closes once with no send/replay. No supervisor/kernel/engine policy changed.

Three suites pass on actual Python3.14.7 and3.10.21: client12/eight omissions,
local descriptions12/eight omissions, AF07-backed descriptions8/eleven omissions.
All strict Rust1.98/2021 warnings/unsafe denial, default Clippy/rustfmt and native
no_std generic-library builds pass. Per-suite native bytes match across both
interpreters. These are not concrete native links, resource fit or execution.
Host tests run actual pinned AF07 service/Owner with synthetic storage over
bounded in-memory channels; no OpenZFS/native IPC/security conformance claim.

Remote tests exercise shared/independent offsets, actual EOF/seek-end, final alias
close, FD and remote-token capacity, invalid names/no transfer, forty directory
open/reject/close cycles, READ-only lookup, per-FD cloexec, known backend errno
preservation and later successful read, lost read body/bad count/unknown final
close with retirement/no replay, both failed local closes and zero/range denial.
Previous local/provider tests rerun against common core. Original client failure/
framing tests rerun plus explicit abort/no-send/no-close-retry. Source diffs and
retention identify the internal Source error-variant rename; no wire/SDK change.

Eight common semantic omissions execute through both actual adapters. Three
remote adapter omissions leak directory handles, widen lookup rights or ignore
client retirement; all fail assertion-based tests. Existing eight client wire
omissions remain detected. That is27 per-interpreter control executions, with
common cases intentionally exercised against both adapters, not27 unique guards.

Initial attempts are retained: local tests referenced now-private SLOTS (fixed to
independent expected13); remote fixture had an unused import (removed, no warning
suppression); omitted initial read clearing survived because the rejection test
reused an already-zero buffer. Stronger dirty-buffer assertions now detect the
omission. Passing code was not weakened and no failed attempt is hidden. A prior
passing local adapter before explicit retirement-state refinement is also retained.

Source-only ten-member candidate:
`build/service-deliveries/filesystem-remote-fds-2026-10-21-v1`, seal
`21639ae14bde1f1e82cdc9c8c6af683a256a238403c517bd8e5c66acf6919a95`.
Includes current common/local/remote/client sources/tests, license, contract and
dependency record. Original5-member descriptor/client and77-member AF07 candidates
stay fixed; no copied engine/SDK, native image, pin/default/authority/limit change,
sibling edit/message, guest or real-prefix installation.

Native continuation still needs exact authenticated process FD/path/binding
messages, cross-process/fork and failed-exec preservation, immutable executable
admission, full sys-init startup/copy/exec/wait/endpoints/readiness/shutdown and
Aether concrete resource-fit/native command/error/cleanup/fresh-boot witnesses.
Readonly open, cached size or digest alone cannot authorize immutable exec.
Packages/Zsh/TTY, independent reviews and full UL-007/081/082/M3/R1 stay open.

Quality/standards/Experience pins and inventory pass, along with actual minimum/
current Python syntax and whitespace. final-source.json and source-changes.diff
bind maintained source/doc changes. All ten attempt roots are retained in verified
archives with full per-member hash/size records before redundant removal:
134742011 logical bytes removed,46476665 archive bytes retained. Physical disk
reclamation was not measured. No historical dependency or evidence was removed.
