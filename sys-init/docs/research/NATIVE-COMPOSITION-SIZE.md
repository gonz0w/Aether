# Native retained-sample composition: size findings

Build-only study, 2026-09-06; BG-058, decision 0080. No candidate was executed on
Aether and no current runtime or compiler default was changed.

## Result

The candidate fits **120 named compiler configurations**, including the two
previously attempted bound stale-prefix cases. Review during decision 0081 found
that the study script substituted receipt_channel for the no-cfg policy, so this
was not every harness configuration. The AST extraction also omitted four
dynamically constructed service-bad-* configurations. The fresh native qualification must also
cover policy and skip-deadline, which use no cfg. The largest image is
**4048 bytes**, leaving **48 bytes** under the unchanged 4096-byte linker bound.
The pure candidate validator also passes all nine named host Rust tests and both
exact omission controls. These results establish feasibility, not target acceptance.

The candidate combines the retained session revision with:

- Rust 1.98.0, edition 2024, `-C opt-level=s`;
- `Sample::new` and `Sample::push` kept out of line, `Sample::state` always inlined;
- the retained explicit 1042 invariant failures in the new session/fixture paths;
- source-path remapping to `sys-init/prototypes/native-supervisor`, preserving
  filenames/line metadata while removing workspace-prefix dependence;
- the existing static relocation, panic-abort, linker/target and all assertions.

`candidate.patch` records exact differences from the current native files. The
newer raw-capture module and its prefix control are included. No source assertions
were deleted to obtain these sizes. Diagnostic changes in the previously unaccepted
session still need review as part of the native acceptance decision.

## Measured comparisons

Same source directory within each comparison; all figures include code and readonly
data in the linker's `.text` output section. Failed strict links still supply maps.

| Source/profile | Held fact | Stale O1 | Stale S | Stale O2 | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| Original retained session, level 2 | 5336 | 4400 | 4472 | 4824 | Does not fit |
| Original retained session, s | 4792 | 4192 | 4232 | 4376 | Does not fit |
| Original retained session, z | 4784 | 4400 | 4472 | 4600 | Does not fit |
| Retained reduced-diagnostic revision, s | 4456 | 3944 | 3944 | 4088 | Held and pending control do not fit |
| That revision plus inlined assertion helper, s | 4440 | 3912 | 3912 | 4200 | Does not fit; O2 regresses |
| Separate validator/state accessor hints, s | 4072 | 3560 | 3560 | 3720 | All 12 selected probes fit |
| Same candidate with normalized paths, s | 4048 | 3536 | 3536 | 3696 | All 12 fit; both build directories produce identical bytes |

The complete assembled candidate also fits all 120 configurations at `s`, with the
same 4048-byte maximum. Optimization `z` was not uniformly smaller; do not infer
runtime speed or a general optimal setting from these results. No timing benchmark
was performed and no production performance claim is made.

## Provenance and limitations

The first invocation called the compiler binary directly and encountered a host
`rust-lld` loader failure for libLLVM; its 36 rejected links produced no valid size
measurements. They are retained in attempt-1 and excluded from the size comparisons.
Subsequent runs used the same rustup-mediated invocation as the functioning native
harness. Original sources were verified against decision 0079's retained manifest
before copying; candidate transformations, compiler/version/options, relevant tool
hashes, raw artifacts, maps and logs are retained. Source/tool hashes were checked
afterward. This is not a hermetic host-library bundle or general reproducibility proof.

Attempts 6 and 7 use distinct absolute build paths of different lengths. All twelve
corresponding raw images are byte-identical after remapping. This proves only that
paired-path comparison for the recorded tool/input set. It does not qualify every
filesystem/path, compiler build or host. The final assembled candidate has only a
48-byte margin and still needs complete actual target compilation/execution.

Current runtime inputs remain byte-identical to decision 0079's 125-case witness.
The candidate is retained under evidence only. Its session borrows Driver and
caller-owned Sample; retention beyond that session, consumer retirement and owner
recovery remain explicit obligations, not consequences of fitting in one page.

## Follow-on acceptance gate

BG-058 next records a versioned experimental retained-sampling build profile and
its compatibility/default policy before changing runtime source. Qualify the exact
assembled candidate on the pinned producer with **127 native cases**: all current
125 oracles and the two bound S/O2 stale-prefix cases, with every original guard and
cleanup assertion preserved. Retain the exact source-path mapping and tool options.
Missing tools, watchdogs, failed controls or over-limit images cannot satisfy this
gate. Recheck the nine development gates and host validator controls after adoption.
Do not claim full launch-to-sampling composition: the retained session still uses
fixture-seeded admitted state. NT-04 malformed native injection, NT-05–07, history
retirement, full launch composition and BG-033 recovery remain open. The study does
not establish a need to change Aether or its image limit.

## Sources

- [Original combined probe and failed map](../evidence/native-raw-sampling-2026-09-06/preflight-builds/attempt-2/sampling_held.map).
- [Retained reduced-diagnostic source](../evidence/native-raw-sampling-2026-09-06/preflight-builds/attempt-3/binding.rs).
- [Installed compiler options](../evidence/native-composition-size-2026-09-06/attempt-2/codegen-help.txt) and [compiler identity](../evidence/native-composition-size-2026-09-06/attempt-2/compiler-version.txt).
- [Study summary](../evidence/native-composition-size-2026-09-06/summary.json), [paired-path comparison](../evidence/native-composition-size-2026-09-06/path-comparison.json), [complete candidate builds](../evidence/native-composition-size-2026-09-06/attempt-8/results.json), and [host controls](../evidence/native-composition-size-2026-09-06/attempt-8/host-results.json).
- [Candidate changes](../evidence/native-composition-size-2026-09-06/candidate.patch), [terminal contract](../specs/NATIVE-TERMINAL-EVIDENCE-V0.md), and [Foundations evidence requirements](../vendor/aether-foundations/v0.1.0/EVIDENCE.md).

## Coverage correction — decision 0081

The original all-configurations description was too broad: attempt-8/study.py
uses `case[1] or 'receipt_channel'`. Its 120 named builds remain valid evidence;
the default no-cfg policy and four dynamically constructed service-bad-*
configurations were omitted. Retained study bytes and manifests are
unchanged. Decision 0081 qualifies the actual full harness, including both no-cfg cases and four dynamic service cases, and records separate comparisons instead of inventing a baseline.
