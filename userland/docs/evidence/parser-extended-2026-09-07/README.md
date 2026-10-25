# UL-062 fixed parser workload evidence

The unchanged parser passes the explicitly selected UBSan workload on host Python
3.14.7 and 3.10.21. Each runs 172038 inputs: 17550 accepted and 154488 rejected.
The three valid seeds, 171360 byte substitutions and 675 wrong-length cases are
fixed in parser-extended.c. Existing semantic controls also pass. The isolated
reserved-byte acceptance defect fails at seed 0 / offset 12 / value 1, exit 90;
the signed-overflow canary emits the expected UBSan diagnosis. All owned process
groups finish with recorded cleanup. No parser implementation change was needed.

The default combined ASan/UBSan mode remains incomplete: the first instrumented
control times out at 30 seconds with no diagnostics, both within the sandbox and
outside it. The final-source default run is retained too. This is consistent with
the previously recorded empty-main ASan timeout, not a diagnosed root cause or
proof that the parser hangs. No automatic fallback or timeout-as-success exists.
The --ubsan-only flag is an explicit partial selection, not ASan qualification.

See [PLAN.md](PLAN.md) for predeclared oracles, limits and amendment, and
[EXTENDED.md](../../../experiments/command-runner/EXTENDED.md) for commands and
recovery. Each attempt below retains exact source/plan snapshots, summary, raw
streams, command environment, compiler/runtime hashes and process cleanup. Built
binaries remain in the named build directories and their hashes are in summaries.
Apple SDK settings/path are recorded; complete host system dependency closure is
not claimed. No dependency fetching or Podman was needed.

| Attempt | Result |
| --- | --- |
| parser-extended-97r3l2ow | Original combined mode, sandboxed: controls timeout; cleanup complete |
| parser-extended-m9lkdva1 | Original combined mode, escalated: same timeout; cleanup complete |
| parser-extended-zx2viezo | Final source, Python 3.14.7, explicit UBSan: pass |
| parser-extended-t5vxkgru | Final source, Python 3.10.21, explicit UBSan: pass |
| parser-extended-qvrgmxqy | Final source, default combined mode: see retained timeout receipt |

Sweep command wall times (owned-process invocation including startup/reap) were
0.131 and 0.132 seconds respectively. These are two observations, not throughput
or performance guarantees. File output caps and per-command timeouts are enforced;
RSS limits, peak memory accounting and a total suite deadline remain open.

Quality checks, new C format validation and help/version/invalid-usage stream/exit
controls are retained alongside the attempts. Sources are snapshot before execution
and checked for drift after successful runs. Existing parser semantic controls and
the new defect witness qualify the test's selected oracles; they do not prove all
parser semantics. There were no escaped parser defects found in this selection.
Independent technical review is pending; no reader or release approval is inferred.

UL-062 stays active: ASan qualification, general fuzz corpora/minimization,
transport/concurrency stress, static analysis, resource metrics/budgets and native
compensation remain required. The fixed mutation coordinates reproduce semantic
failures; sanitizer-only failures still need isolation. Retain all attempts under
the project's evidence policy. The complete manual weekly suite is not yet ready.
