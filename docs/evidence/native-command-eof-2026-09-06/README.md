# Truncated launch evidence — 2026-09-06

Final pass: 30 command cases, 9 inherited-launch cases and 6 connection cases.
Kernel host checks, 67 Python tests, three release-pin checks and workflow
validation pass. Final formatting checks pass.

Seven parent-live EOF cases send 0, 1, 4, 16, 31, 32 or 383 bytes, close only the
sending endpoint and require exact broker result 1100 + length/reclaimed 0, with
no worker terminal records. The broker checks unchanged aliases and positions
before reporting. The zero-padding mutation is caught after the parent drains
the forbidden reply, exits 104, and broker reports 970. Exact records are required;
a timeout, unrelated panic or partial-reply failure cannot pass.

[Contract/test plan](../../NATIVE-COMMAND-IO.md#truncated-launch-test-plan).
This proves fatal pre-admission rejection, not cleanup, reconnection, unknown
outcome resolution or peer-exit races. No kernel ABI, dependency, quota, sibling
implementation or consumer pin changed.

[Initial attempt](../native-command-eof-initial-2026-09-06/README.md) is retained
with its own archive: all native/host runs passed, but a comment-format check
failed. The final source fixes that and drains the complete forbidden reply to
avoid exit/transport timing dependence. All selected suites were rerun on final
frozen bytes. There was no unexpected native failure or timeout in either attempt.

`results.json` binds suite reports and final source archive. Profile directories
retain raw serial/build/static-analysis logs, native payloads, client/kernel ELFs,
raw broker images and maps under 2 MiB. ISOs are omitted and rebuildable; original
complete output paths are recorded. Source, tests, contracts and approved standards
snapshot are archived; external SDK/tools are separately bound by suite receipts
and digests. This is producer/QEMU evidence, not independent consumer or hardware
acceptance.

`*-attempt.json` records exact commands, UTC start/end and exit status captured
around each run. Pinned format commands and outcomes are in `format-attempts.json`
and `format.log`: approved C configuration for new code, existing LLVM helper
format, Rust 1.98.0 edition 2024. Full standards compliance and extended testing
remain separate as recorded in DEVELOPMENT.
