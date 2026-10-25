# Direct cat admission/startup — 2026-09-07

The opt-in cat_admission owner selects the first image capability, validates its
fixed cat/LC_ALL=C Args template before reservation and invokes the existing native
factory for slot0. The backend remains slot1; this direct-owner experiment requires
four native reclaims across two generations. It is not a new runner request frame,
caller-driven registry, Toybox binary or userland parser implementation.

The exact same gate rejects changed name (-2), argc, environment or unused string
padding (-22) before allocating transport. Native admission then rejects actual
argc5 with EINVAL while preserving reserved transfer endpoint ownership. Valid
admission transfers those endpoints; attempts by the owner to close them return
EACCES. The owner overwrites its local Args storage before role delivery. The
client waits for AECAT001, then independently checks complete argv/env terminators
and private TLS. No mask or initialization operation is replaced by a success stub.

Cases admit-copy/empty/short retain independent input/output/diagnostic, position,
close, EOF, stale backend and native-reclaim verification. Admit-rights rejects
malformed third-role rights at bootstrap110 with no I/O. A name-gate bypass must
reject at1510 before client admission; changed argv after the gate must produce
client109/owner1501 before input reads. These are explicit controls, not generic
panic/watchdog acceptance. See [contract](contract.md) and
[NATIVE-CAT](../../NATIVE-CAT.md#direct-owner-selected-admission).

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use --connections/--inherited-launch with the same SDK/lock for regressions. Host
checks use `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`. Scoped C/Rust formatting and workflow checks accompany them.
Receipts retain actual tool/SDK/source/image/flag identities; timing files record
run UTC boundaries, not per-case timestamps. Source snapshots retain the selected
conformance image; its name does not attest to upstream Toybox provenance.

## Limits

This closes the direct-owner startup prerequisite only. There is no actual
Toybox selection/adaptation, caller-supplied admission, invalid-invocation diagnostic
or completed CAT row. Native SDK initialization, error/unknown reply handling,
Toybox callbacks/flush/finalization and abnormal stop remain to qualify. Userland
owns its parser/patch/SDK and independent consumer pin/review/build. Original
UL-059 return bytes, release pins and siblings stay untouched; R1 remains open.

## Final qualification

All runs pass on their first attempt: 158 command cases (152 prior plus six direct
admission cases), six connections and nine inherited-launch cases. All 98 Python
tests, Zig tests, offline pins/workflow and scoped C/Rust formatting checks pass.
The three receipts match final frozen runtime sources. All 34 kernel/build inputs
and SDK/libc/tool-lock identities match the prior role qualification. The largest
new admission owner is 5,784/8,192 bytes; no limit was raised.

`final-artifacts.tar.gz` retains frozen sources, generated/native envelopes,
compiled clients/backends and raw logs. ISOs, duplicate installed boot files and
kernel.elf are omitted, with build/ISO receipts retained. `qualification.json`,
timing files and manifest bind this evidence. No failed attempt was observed or
discarded; per-case timing, independent review and extended-stage coverage remain
explicit limitations. Archive identity does not substitute for consumer acceptance.
