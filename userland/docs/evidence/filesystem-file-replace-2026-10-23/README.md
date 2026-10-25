# Exact-target FILE replacement —2026-10-23

[Pre-code contract/security/simplicity review](../../proposals/FS-FILE-REPLACE.md).
From userland: `python3 -B experiments/filesystem-service/check-process-descriptors.py --in-place --replace`,
and add `--paths` for the combined candidate.41 selected/42 combined cases pass,
including all37 prior producer cases (plus the selected path counterpart), with
19 compiling semantic controls in each. Tests execute actual ProcessFiles/Remote/
sealed AF07 service with synthetic host storage, not injected native authority.
Strict Rustfmt/Clippy/host and freestanding libraries pass. New code adds no unsafe,
fields, allocations, rights or quotas. Native complete-owner fit/runtime, FILE/C
wire consumption and public dup2/stream replacement remain open; no new VM.

Full13-slot replacement needs no spare FD/handle/description. Exact chosen target,
source/unrelated CLOEXEC, shared offsets, self/same-description/empty target,
inherited last-reference retention, stale/settled keys and malformed indices are
checked. Failed last-handle close retires every view/source once with no usable
published replacement or replay. This is a lower Rust primitive, not a POSIX
recoverable-error or public redirection claim.

[Results](results.json) retain exact input/tool/source/recipe hashes and controls.
[Attempt1](attempt1.json) fails strict compilation for an unused test storage field;
actual storage-counter assertion supplies meaningful observation. [Attempt2](attempt2.json)
fails Clippy duplicate_mod: reuse the parent process fixture instead of loading a
second copy or suppressing the lint. Production replacement body did not change
for either test fix. All generated test/binary/source trees and launcher logs were
removed after complete child cleanup; no passing transcript/archive is retained.
Only current Python3.14.7 ran; minimum3.10 coverage is missing. Technical review by
implementation agent; independent/native/release acceptance pending.

[Type-layout measurement](view-layout.json) uses the actual Option<Descriptor>
type with pinned Rust:2 bytes per slot, four13-slot arrays104 bytes versus four
16-slot arrays128, delta24. It allocates/selects no larger runtime profile and is
not a measured complete-owner fit. The first unused-constructor probe failure is
preserved in view-layout-attempt1.json and its assessment; final strict probe passes.
A separate16-alias view with only13 shared descriptions/16 source bindings is
proposed to resolve the mixed C16-slot/remote13-slot mismatch; implementation is
pending maintainer disposition under the current-limits instruction. Existing
profiles, wires, code/data/stack/backing/channel/worker/workload/time limits stay fixed.
