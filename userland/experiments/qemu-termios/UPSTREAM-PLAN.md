# UL-069 upstream tr regression review

Uses CONSUMER-PLAN.md's Linux-only scope, quality CP/TD/TE requirements,
owned adapter, 512 MiB/32 PIDs, read-only inputs, network/capability restrictions,
source retention and pending review disposition. Each of three containers has
180 seconds. No new upstream test semantics or package selection.

Run unchanged GNU tr.pl/Coreutils/CuSkip with pinned Perl helper files and
notices, then the existing exit99 control; require exactly the full 134-case
inventory and existing exit/stdout/stderr oracle. Run unchanged BusyBox tr.tests
and testing.sh with original feature flags and image echo helper; require exactly
five PASS lines, no FAIL/SKIPPED and exit0. This remains a stdout-only upstream
BusyBox harness. Preserve BusyBox executable basename and explicit applet argv.

Verify source archive, binaries and staged QEMU/runtime hashes. Select the same
image as the direct PTY witness. Capture runtime identities and raw output,
verify owned cleanup, run syntax and quality checks. New adapter review remains
pending; these regressions do not qualify native TTY, missing locales, static
fault injection or broaden the command-runner migration scope.
