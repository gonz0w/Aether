# 0198: Exercise the canonical mixed FD table through our dispatcher

2026-10-21 / BG-067. Consume userland's32-member stream-replacement candidate
5b43ec90ed2481b618d0b23e4801b9dde18d5997bbcd319e611f984824cd7183
and its ten exact dependency deliveries. Verify full membership and hashes before
copy/build; preserve accepted owners, prior evidence, runtime/release/default pins.

Requirement: one host C process uses the actual canonical bindings/table/routing/
pipe/write/replace helpers and actual C file transport against sys-init's actual
Peer/handler/process/AF07 service with synthetic storage. Deliberately overlap
file selector3 and pipe selector3 while logical descriptors differ. Prove file
bytes never fall through to stream callbacks, real host pipe creation/read/write,
stream aliases and last close, chosen empty-target redirection/flag behavior and
FILE replacement refusal. Check file shared offsets, EOF, final close, lost read
body, stale map and unknown stream-close outcomes both with/no physical effect.
Unknown outcomes preserve metadata and retire admission without replay; fixture
owner separately closes unresolved actual host pipe ends. Keep independent server
source counters, cleared buffers, raw endpoint results and stopped processes.

The simpler alternative is trusting producer helper tests or routing by number.
Producer evidence does not exercise our exchange wrapper; numeric routing is
incorrect for overlapping selectors. Choose one small host consumer over delivered
helpers and reuse existing server App/fixture/driver; no runtime FD ledger, new
wire, generic service machinery or native adapter is added. No obsolete accepted
path is removed. Existing files and source closures stay fixed.

Validation: strict C17/UBSan/format, strict Rust2024/default Clippy/format on the
new server fixture, focused live positive/failure cases and three assertion-specific
compiling omissions. Exact tools/headers/resource/runtime/native Rust library
inputs pin before build and recheck afterwards; owned60s/4MiB compile bounds and
30s paired-session watchdog/owned group cleanup. Full offline checks required.

Host pipes and synthetic storage only. No actual console, native authority/IPC,
selected shell/startup, POSIX dup2, copy/exec/failed-exec, code/stack/heap fit or
native acceptance. Native helpers and full startup/descriptor ownership selection
remain userland/Aether inputs; sys-init retains full dispatcher/readiness/shutdown
integration once selected. No sibling edits/messages, new guest or quota increase.

## Result

[Evidence](../evidence/mixed-fd-consumption-2026-10-21/README.md) records all12
selected source closures/277 hashes and fresh host builds. Five live positive/
lost-body/stale-map/unknown-close/no-effect-or-effect cases pass. Three strictly
compiling selector/alias-close/unknown-close omissions fail exact C assertions.
Actual OS pipe ownership/EOF/close and synthetic AF07 service source counters are
checked independently. All owned processes stop, normal service threads join,
strict C17/UBSan/format and Rust/Clippy/format pass; input/tool/header/runtime bytes
match after use. No runtime source or historical packet changed. Documentation
impact: update the existing API, current handoff/planning and quality surface.
