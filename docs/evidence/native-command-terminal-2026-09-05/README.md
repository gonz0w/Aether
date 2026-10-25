# Command terminal-kind extension — 2026-09-05

[Contract](../../NATIVE-COMMAND-IO.md#terminal-kind-extension).
Twelve final command cases pass: the original nine plus normal-nonzero,
child-fault and fault-as-exit. Normal return 134 and actual #UD (detail 134/kind 2)
happen after output with both inherited child aliases live. Each successful
scenario requires exact terminal sequences across two generations and six
reclaims. Both abandoned aliases are removed on observed termination, real output
and input preservation are checked, and consuming collection remains parent-owned.
Misreporting the fault as normal is rejected with exact child/parent/broker context.

Fifteen targeted regressions pass: inherited-launch 9 and connections 6.
Kernel/host checks, 56 Python tests and three offline standards checks pass.
Python compilation and scoped C/Rust formatting pass. Kernel hashes match the
original command-I/O snapshot. Other file, memory, SMP and default-boot suites
were not rerun. The base broker remains 6936 bytes within 8192.

`summary.json` pins the 27 accepted native cases, tools, reports and 178 source
files. `producer-sources.tar.gz` contains those source bytes. Suite directories
retain ELFs, raw brokers, envelopes, maps, build and serial logs. Large ISO files
remain at recorded local output paths and are hash-identified in the reports.
Final command suite: `zig-out/command-runner-suite-cxqoc3zp`.

Initial iterations caught variant link maps overwriting the base map and a
partial diagnostic-line oracle that did not match the complete variable-address
fault line. Both were corrected; the final oracle uses exact stable terminal
records. Regression runs on earlier harness bytes were superseded by the final
15-case rerun. Only the final source-matched reports above count as acceptance.

This extends local producer evidence; it does not supersede the original
`native-command-io-2026-09-05` bundle, change consumer pins, edit sibling code or
claim independent adoption. Faults at other I/O phases, explicit stop, malformed/
lost reply handling tests, unknown-outcome recovery, POSIX signal/wait mapping,
public runner policy and package reconstruction remain separate work.
