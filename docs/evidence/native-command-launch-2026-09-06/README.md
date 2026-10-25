# Complete malformed launch evidence — 2026-09-06

Pass: 22 command cases, 9 inherited-launch cases and 6 connection cases. Kernel
host checks, 67 Python tests, three release-pin checks and workflow validation
pass. One attempt per suite, no unexpected failure or retry.

`malformed-launch` rejects a fixed 22-entry corpus in each of two generations
(44 requests): exact errno, zero receipt/reserved bytes, then valid same-connection
launch, normal child output/status and broker 100/reclaimed 6. The corpus covers
version/count bounds, header/entry reserved bytes, command-name padding,
unterminated/padded argument/environment strings, environment allowlist and unused
slots. Earlier cases continue to cover authority and admission failures.

`allow-launch-version` deliberately bypasses version validation in an isolated
broker. The same parent catches its improper success at exit 103, then broker
970/reclaimed 0. The oracle requires these exact records; expected workload
rejection is not an unexpected product failure or a recovery claim.

[Contract and test plan](../../NATIVE-COMMAND-IO.md#malformed-launch-test-plan).
Normal validation stays before allocation. Successful retry and backend checks
witness preserved framing, sufficient launch capacity and unchanged offsets/data;
they do not establish unlimited rejection endurance, generation refunds or partial
frame/EOF recovery. No kernel, quota, dependency or sibling pin changed.

`results.json` binds reports and final source archive. Profile directories retain
raw serial/build/static-analysis logs, payloads, client/kernel ELFs, broker bytes
and maps under 2 MiB. ISO images are omitted and rebuildable; complete original
output paths remain in the summary. The archive includes source, tests, contracts
and approved standards snapshot, but external SDK/tools remain separately pinned
by suite receipts/digests. It is producer evidence, not consumer/hardware acceptance.

`*-attempt.json` records exact commands, UTC start/end and exit status captured
around each run. Sources stayed frozen through all qualified checks. Pinned format
commands/results are in `format-attempts.json` and `format.log`: approved C style
for the new probe, existing LLVM style for the helper, Rust 1.98.0 edition 2024 for
the broker. Full standards compliance and extended testing remain separate work.
