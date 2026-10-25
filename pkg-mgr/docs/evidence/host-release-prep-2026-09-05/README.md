# Host release preparation evidence

HR-01 defines the first macOS arm64 experimental private-root host scope.
HR-02 fixes a source-rejection test: POSIX errexit does not stop on a standalone
negated command. The new check requires grep status 1 and rejects both a forbidden
extraction marker and grep errors. A disposable grep adapter returning success for
extract-start demonstrated the old script exits 0 and the corrected script exits 1.
No product bypass was introduced. CLI fixture nested-if spelling and CDPATH quoting
were corrected; all four changed shell files pass ShellCheck 0.11.0.

HR-03 adds a default 600-second watchdog. Six controls cover success, nonzero child
status, timeout with a TERM-resistant descendant, leftover child rejection, signal
cleanup and missing executable. Heartbeat cessation checks actual descendant work,
not platform-specific zombie PID visibility. Logs are retained in an owned private
run directory, including successful attempts. Tests must not escape the owned process
group; this is not a sandbox. Current syntax/lint and control results are attached.

The initial full run is rejected: its runner source was changed while the shell
was reading it, and its output contains an unexpected-EOF diagnostic despite a
zero child status. `initial-incomplete.log` preserves that attempt. It is not passing
evidence. The final run uses frozen runner sources and must contain the explicit
sixteen-fixture completion marker. Zero process status alone is insufficient.

No full-repository lint, fuzzing, manual, independent reviewer or release acceptance
is claimed. Remaining HR-02 and HR-04–HR-08 work stays in the release plan.

The frozen rerun passes all sixteen fixtures and three standards checks. The final
completion qualifier was added afterward and tested directly: it accepts this raw
log, rejects the initial incomplete attempt with 125, rejects missing/partial markers
and preserves a nonzero child status. Final watchdog controls and syntax/lint pass.
The remaining unmodified shell baseline has 108 diagnostics, retained without
suppressions in shellcheck-remaining.log. No third full runtime run was needed for
the isolated report-qualification change.
