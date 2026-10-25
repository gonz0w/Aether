# Matched phase-one command-runner qualification — 2026-09-13

Requirement: run the complete command-runner suite on the exact frozen runtime
inputs used for the 287-case argument/signal connections qualification. Preserve
startup/custom-handler/mask and syntax positives and semantic controls. Aether owns
producer evidence; userland owns independent acceptance and UL-081 SDK integration.

Forbidden: source edits during qualification, combining mismatched revisions,
counting timeout/boot failure as rejection, installing private adapters, modifying
sibling repositories or released standards/evidence, or claiming full dash/R1.

Selection: verify source, SDK and tool-lock identities; run unchanged complete
command-runner with an owned 1800-second deadline and existing per-guest watchdogs;
retain all outcomes and artifacts; verify frozen sources after execution and link
the matching connections receipt. Existing host qualification on those same inputs
is retained in the phase-one handoff; run current host checks before closing.

No new runtime behavior, ABI, authority, quotas, buffers, unsafe boundaries,
dependencies or concurrency mechanisms. Foundations E-01–E-08 and local DEVELOPMENT
apply. Simplicity: reuse the existing suite and sealed input archives rather than
add another test runner or duplicate source/SDK bundles. No runtime paths retired.
Documentation impact: record results and next action in STATE and companion index.

## Failed matched-input attempt and scoped correction

The first complete command-runner attempt failed before QEMU in 37.79 seconds.
The late backend-open recovery owner links to 8,200 bytes, eight over its unchanged
8,192-byte limit. Its linker assertion correctly rejects the image. All original
256 source hashes remained unchanged. The diagnostic link map is retained.

Correction selection, before code: prevent inlining of the shared scalar control
wrapper for command-runner owners, as already done for fork-dispatch. Repeated
syscall setup should share one function body in this size-bounded fixture. Preserve
all arguments, rights, return values, cleanup and the two-page linker assertion.
No new wire format, service, option, unsafe operation or resource quota. This is
compiler layout control, not removal of checks. Simpler than raising the limit or
special-casing the late-open test. No obsolete runtime path is removed.

Inspect size with the exact failing recipe first; if it fits, freeze the one-line
change and run both complete command-runner and connections suites plus host and
Rust formatting checks. The original handoff remains immutable and failed on its
command-runner replay; a corrected source delta and new matching receipts are
required. Do not advertise its old source set as passing the combined gate.

## Result and corrected consumer intake

PASS: all **431 command-runner cases** (1456.04 seconds) and **287 connections
cases** (926.51 seconds) on the same frozen source set, strict SDK and tool lock.
Both suites ran concurrently in separate owned output directories; timings are
qualification receipts, not performance baselines. Host checks and Rust formatting
pass. Simplicity manifest/four members verify; released pins are unchanged.

All 256 runtime/test sources stayed frozen during these runs; both native reports
bind the same 242 harness sources. The only change from the original handoff is
`cfg_attr(any(fork_dispatch, command_runner), inline(never))` on `ctl` in
`user/native-connections/supervisor.rs`. The late-open owner now occupies 7,816
bytes; the largest shell-role owner is 7,880, within the unchanged 8,192-byte limit.
All 547 compared connection ELF/raw images are byte-identical to the previous
qualification, and the entire connection suite was nevertheless rerun.

Ten independently checked native trace sets cover syntax and its two controls,
arguments and its three controls, and signals and its two controls. Syntax retains
exit2/backend17 twice and four reclaims; its skipped-main and skipped-close controls
retain exact 1501/1503 rejection. Arguments/signals retain actual child/parent0,
backend17 and six reclaims, with their original exact rejection controls.
`startup-cases.json` indexes all 208 startup cases, including custom handlers,
mask bridging, saved-frame validation and deliberate broken implementations.
This is producer qualification using the existing oracles, not independent review.

`qualification.json` and the complete native result files identify final artifacts
and counts. Archives are read back member by member against their hash indexes.
The original failed attempt, diagnostic map and size preflight are retained; it
was a build rejection before any guest ran, not a timeout or runtime failure.
No attempt was discarded, and the original handoff/sealed evidence is unchanged.

For independent intake, use this packet's **sources.tar.gz and sources.json** in
place of the earlier signal packet's runtime source archive. Use the original
[phase-one support/SDK handoff](../dash-phase-one-handoff-2026-09-13/README.md)
for `support.tar.gz`, the archived strict SDK, tool/boot setup and commands.
This packet's `inputs.json` pins those references. Restore support first, then the
corrected runtime archive into a fresh owned checkout, and verify all final source
hashes before running both unchanged commands. Preserve upstream licenses and
the confined SDK Makefile link. Do not install private fixture adapters into the SDK.

The original support archive includes the previous progress documentation; this
README and current STATE supersede its historical next-action text. Runtime/build
inputs remain explicit. Independent userland replay and UL-081's supported SDK
boundary review remain open. The full twelve-workload matrix, arbitrary filesystem
shell, OpenZFS and sys-init/package release assembly are not completed by this run.

Next qualify the unchanged phase-two wait/failed-exec/descriptor workloads while
userland can independently consume this matched producer set. Keep its acceptance
separate from producer progress. No sibling files or released standards pins changed.
