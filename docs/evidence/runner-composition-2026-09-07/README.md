# Four-role terminal and startup composition — 2026-09-07

The AERIO001 fixture now composes selected nonzero/fault results and logical
AERUN001 startup with explicit runner/child roles. Actual normal134 stays134;
actual fault134/kind2 maps to parent1. Collected kind/detail come from the observed
native terminal. Child aliases intentionally remain live at termination; owner
retirement happens only after terminal plus drained request EOF. Parent closes,
backend readback/stale denial and two generations/six reclaims remain required.

Three-string normal0, six-string normal64 and six-string fault134 forwarding
cases use the existing independent child argv/environment observer. It verifies
empty and 31-byte values. The parent copies validated carrier slots to the launch
request and overwrites the request before child bootstrap. The selected slot1/2
is a fixture input, not the actual userland parser's selection logic.

Five positive cases: `success-exit134`, `success-fault`, `success-forward`,
`success-forward-wide`, `success-forward-fault`. Four controls force zero or ignore
fault kind (1401), corrupt the fourth argument (child80, owner1407), or omit owner
alias retirement (1403). Generic panic/watchdog does not satisfy these checks.
See the [preimplementation contract](contract.md) and
[interface reference](../../NATIVE-COMMAND-IO.md).

## Failed attempt

Attempt1 stopped before QEMU because a variant link overwrote helper3.map. The
baseline public-musl check then inspected the fault variant, whose unused close
function was legitimately removed, instead of the baseline child. This is a
harness artifact-isolation failure. Each variant now writes a distinct linker
map; the baseline check is preserved. Frozen source and artifacts remain in
`attempt-1.tar.gz`, with exact run boundaries and failure log alongside it.

## Reproduction and scope

Run `python3 scripts/launch_smoke.py --command-runner` using
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use `--connections` and `--inherited-launch` for selected compatibility checks.
Run `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
plus scoped C/Rust formatting and workflow checks. Timing files bind exact final
run boundaries; per-case timestamps and extended-stage evidence remain missing.

No kernel/ABI/resource limit, dependency, release pin or sibling repository changes.
Independent consumer build/review, malformed combined startup, unknown collection,
remaining RL coverage and immutable handoff remain open. UL-059/067 and R1 are not
accepted by these bounded producer witnesses.

## Final qualification

Attempt2 passes all 136 command cases (127 existing plus five positive/four broken
composition cases). Six connections and nine inherited-launch regressions pass.
All 98 Python tests, Zig tests, offline standards/pins, workflow and scoped format
checks pass. All three receipts match the frozen runtime sources; all 34 kernel/
build inputs and SDK/libc/tool-lock identities match the previous qualification.
Largest owner: 7,824/8,192 bytes; no limit was raised.

`final-artifacts.tar.gz` retains source snapshots, carrier bytes, binaries,
envelopes and logs. ISOs, installed boot duplicates and kernel.elf are omitted;
build/ISO receipts remain. Timing files record exact run UTC boundaries, with
per-case timing and independent/extended evidence limits still explicit.
`qualification.json` and `manifest.json` bind retained results. The read-only
[handoff scope review](next-review.md) identifies the next audit without claiming
consumer acceptance or requiring general unknown-result recovery in this slice.
