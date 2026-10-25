# Public signal routing source review

Documentation-only review on 2026-09-08. See the
[current contract review](../../NATIVE-SHELL-STARTUP.md#public-signal-routing-review--2026-09-08)
for coverage, compatibility issues, bounded next implementation and release gates.

`inputs.tar.gz` retains 11 exact local/sibling source inputs; `inputs.sha256`
identifies each member by path relative to the DEV directory. Every archived
member was read back and verified against its SHA-256. Sibling checkouts were
read only. This packet introduces no build dependency on those checkouts.

Validation: `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` passed, including 98 Python tests and offline pin/workflow
checks; see host.log. The simplicity input manifest matched
`8c3d8095acc9b6283a5f6970bc4ce6e7e4646a04fb759f8cf2940ed494cbeff8`
and its four members passed `shasum -a 256 -c SHA256SUMS`.
No fresh QEMU qualification was selected for this documentation-only review.
The prior 284-case packet retains its original scope and bytes.

Exploration corrections: one sed range typo failed; a search initially used
kernel/native_pending.zig rather than kernel/arch/x86_64/native_pending.zig.
The first simplicity verification used the parent directory and failed to locate
SHA256SUMS; rerunning from inputs/ passed. These were read-only inspection errors,
not failed runtime or host qualifications.

No runtime implementation, consumer acceptance, independent review, release-pin
update or full-dash handoff is claimed. Current progress stays in STATE.
