# Bounded extra-argument diagnostics — 2026-09-07

The direct cat conformance client rejects an extra argument before input I/O,
returns 64, leaves stdout empty and delivers the exact 37-byte ASCII/LF proposal
`cat: this profile accepts stdin only` to its private diagnostic role. This text
is Aether-authored and is not an upstream Toybox message or accepted userland CLI.
The owner checks exact bytes, zero stdin/stdout requests, all three closes,
terminal EOF, stale backend denial and four native reclaims across two generations.
Status 64 alone cannot satisfy the oracle.

Eight templates cover `-`, `-u`, `-n`, a filename, `--help`, `--version`, an unknown
option and an empty argument. Short writes must continue the remaining suffix.
Malformed diagnostic rights retain bootstrap 110 with no diagnostic or input I/O.
Four deliberately broken clients skip or corrupt the diagnostic (owner 1505),
attempt an input read (1520), or skip a close (1503). These cases require the exact
semantic rejection; a generic panic or watchdog is not acceptance.

See [pre-code contract](contract.md), [text identity](text-identity.json) and
[local contract](../../NATIVE-CAT.md). The owner copies a bounded argc2 startup;
this adds no kernel ABI, authority, registry, resource limit or dependency.

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use `--connections` and `--inherited-launch` with the same SDK/lock for regressions.
Host checks use `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`. Experience, workflow and scoped C/Rust formatting checks
accompany these runs. Timing files record run UTC boundaries; per-case timestamps
are unavailable.

## Limits

This qualifies a producer conformance client only. Actual Toybox/SDK adaptation,
producer I/O failure and uncertain finalization witnesses, abnormal stop and
independent userland review/build remain open. No completed CAT row, UL-067
consumer acceptance or assembled R1 readiness is claimed. Existing nonzero status
is retained during cleanup, but injected delivery/close failures are not qualified
by this slice. UL-059 remains at its independent consumer handoff boundary.
Release pins, the prior handoff bundle and sibling repositories stay unchanged.

## Final qualification

All first attempts pass: 172 command cases (158 previous plus 14 new), six
connections and nine inherited-launch cases. All 98 Python host tests, Zig tests,
offline pins, Experience, workflow and scoped C/Rust formatting checks pass.
All three receipts match final frozen runtime sources; 34 kernel/build inputs
and SDK/libc/tool-lock identities match the preceding admission qualification.
The largest new owner is 5,776/8,192 bytes; no limit increased.

`final-artifacts.tar.gz` retains frozen sources, argument artifacts, compiled
clients/backends, native envelopes and raw logs. ISOs, duplicate installed boot
files and kernel.elf are omitted with receipts retaining their identities.
Qualification/timing files and the manifest bind this evidence. No failed attempt
was observed or discarded. The prior bundle's artifact hashes were independently
rechecked. Per-case timestamps, independent review and extended-stage coverage
remain unavailable; archive identity does not establish consumer acceptance.
