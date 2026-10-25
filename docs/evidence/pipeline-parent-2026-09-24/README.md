# Parent-driven dash workloads — 2026-09-24

The unchanged consumer `pipeline.sh` and `early-reader.sh` now execute through
actual pinned dash main/init/job construction in the parent. Both pass the full
101-case capacity suite, including their semantic rejection controls. Final358-case connections and431-case runner qualification also pass on the
same287 runtime sources:890 native cases total. Matching host checks pass105 Python
tests plus Zig/Rust. See retained attempt reports.
This is producer evidence for the last two scripts in userland’s 12-script matrix.
Userland’s independent acceptance remains 10/12 until its own replay and review.

## Behavior and authority

Dash creates the pipes, forks the children, maps standard descriptors, executes
the unchanged helper bodies and collects its jobs. The pipeline captures exactly
`pipe data\n`, with three child collections. Early-reader consumes one byte, obtains
EPIPE after the reader closes, verifies pump status42 through pipefail and captures
exactly `epipe ok\n`; only its two copied children are collectible. The third capacity
peer remains unrelated. Each positive repeats three generations with15 domain
reclaims. Descriptor numbers remain separate from generation-bound pipe holdings.

The parent receives a scoped read-only /work directory view and checked advisory
identity. Fork readiness uses authenticated rebound channels. Exec accepts only the
pinned helper roles and a validated four-entry environment profile; unknown vectors
are rejected. Parent output, descriptor close, directory queries and waits share the
retained dispatcher. Collection is once-only; terminal confirmation precedes cleanup.
No authority comes from a path, PID, local fd or environment string alone.

The new profiles enable existing native public signal actions and copied dispositions.
A required SIGCHLD query verifies routing before main. The early helper uses actual
musl signal(SIGPIPE,SIG_IGN). Earlier copied-main evidence linked musl signal calls
without enabling this native routing. Those sealed artifacts are unchanged; their
signal-operation claim is narrowed here. This does not establish general signal/TTY
semantics or generated SIGPIPE delivery under the default disposition.

Controls retain exact outcomes: changed script byte2743, leaked fd10 alias2733,
bad environment selector2746, wrong EPIPE errno helper98/owner2726, and disabled
public signal routing parent138/owner2730. Every control requires zero reclaims;
a timeout or generic panic is not acceptance.

## Attempts and regression scope

- Attempt1: compile failure from a legacy-only fallback local; fixed preprocessor scope.
- Attempt2: child136/owner2607; fork channel preparation belonged in the real copy
  hook, not the manual driver. Corrected the fixed launch ABI environment slots4–7.
- Attempt3: focused pipeline passed, but lacked public signal routing; not final evidence.
- Attempt4: early helper97/owner2726 exposed that missing signal route.
- Attempt5: focused early-reader passed with signal routing enabled.
- Attempt6: all101 passed. Header formatting check identified three line wraps;
  formatting was deferred until the frozen run completed.
- Attempt7: all101 passed after formatting. All142 ELF/raw programs are identical
  to attempt6. Host checks pass105 Python tests plus Zig/Rust, including three exec
  decoder configurations and scoped directory-owner rejection tests.
- Attempt8: all101 pass on the final source set after the runner assertion fix.
  All142 ELF/raw programs remain identical to attempt7.
- Connections attempts1/2: all358 pass, including final matching-source qualification.
- Runner attempt1: six cases passed, cat-roles-startup failed client62/owner1501.
  Its stale assertion required EINVAL for unused getpid registers. An isolated
  corrected-source probe passed. The replacement checks actual caller identity
  even with four nonzero unused registers; kernel behavior is unchanged.
- Runner attempt2: all431 pass, including the existing identity/descriptor/signal
  controls. Final pipeline, connections and runner reports match287 runtime inputs,
  the same tool lock and libc receipt.

The retained reports bind commands, sources, tools, cases, artifacts, firmware/VM
invocations and raw serials. Failed and selected-case attempts are not full passes.
The older launch harness does not record per-case timestamps/durations. Log file
creation/last-write intervals are retained as filesystem observations, not precise
execution timing or performance evidence. Final observed connections/runner
intervals are1172.47/1470.80 seconds, within the1800-second review ceiling. Runtime
inventories exclude Finder metadata; older launch reports also hash five
.DS_Store files. Initial and final metadata snapshots are both retained: user/.DS_Store
changed between runs while all287 runtime inputs match. The first finalizer incorrectly
expected the earlier metadata; finalization-correction.json preserves that analysis
failure and the exact correction. No native oracle was changed. No released pin changed.

Relative to the previous natural-fds suite, all48 existing client ELFs are unchanged;
77 of78 Rust owner raws changed after the new compile-time paths. All prior cases
are rerun; do not infer byte-identical compatibility from a passing suite.

## Resources and limits

The parent pipeline owner is17960 bytes and early-reader owner18392, below the24-KiB
limit. Linked text equals the qualified raw programs. Reviewed critical depth is
3968/4088 bytes for pipeline and3984/4088 for early-reader, leaving120/104 bytes.
This is a scoped linked-call audit, not a general stack proof. Native C workers have
their separate existing stack. No kernel/SDK ABI, shared pipe core, resource budget,
dependency or sibling repository changes are part of this integration.

The facade is private and bounded: fixed helper paths/roles, four environment entries,
read-only /work view and the existing worker limits. It runs scripts with `sh -c`.
It is not an interactive shell image, arbitrary argv/env support, general process
service, POSIX certification, SDK publication or consumer-owner approval. Earlier serial exec/substitution sessions remain qualified separately; this packet
does not compose them with the new pipeline owner. Broader signals/TTY, shared
serial-shell assembly, persistence/OpenZFS, packages and sys-init remain
R1 work. Independent build/reviews and extended reliability/security gates remain open.

## Consumer replay

Verify SHA256SUMS and the source/artifact manifests before consuming the packet.
The two script pins are copied unchanged from the consumer workload directory;
consumer-match.json records their exact expected-output hashes. Existing native
main/jobs and helper pins remain checked offline by the harness. Use the matching
SDK and tool lock identified in the reports, not an arbitrary mutable SDK.

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

For diagnosis only, append `--case` with the full case name ending
`pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent`
or that name plus `-early`. A selected case is never full-suite coverage. Independent
review must compare actual child status/output/cleanup and named negative outcomes,
then record its own acceptance; this packet does not update another owner’s matrix.

Artifacts are archived and readback-hash-verified before removing only their generated
duplicates. Prior sealed evidence remains untouched. archive.py records that process;
per-attempt cleanup receipts identify exact paths, counts, bytes and archive digests.
