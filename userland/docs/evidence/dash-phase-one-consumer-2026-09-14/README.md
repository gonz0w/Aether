# UL-007 matched phase-one consumer qualification

The corrected phase-one handoff passes independent local execution on 2026-09-14:
**431 command-runner and287 connections cases, 718 native cases total**, on one
frozen restored source set and the pinned SDK. Host checks pass, including100
Python tests plus Zig/offline checks. All208 startup cases are indexed and ten
separate syntax/argv/signal lifecycle trace comparisons pass.

Both native receipts bind the same242 harness source hashes. All602 restored
source/support file hashes and4311 SDK file hashes remain unchanged. The producer
seal is f375684f43d3daf8fb0b2811c2dd403f21c10a67e42e1b89a0d068529e2a35d4.
Support was restored before the corrected runtime archive. Existing local SDK
bytes match the producer index and prior tool/libc/musl receipts; no private
adapter was installed. Both suites use separate owned output directories and
retain complete cleanup receipts. Their timings are observations, not a benchmark.

This is fresh matched evidence for startup/custom handlers/mask handling and the
unchanged argv, signal-table and syntax workloads. Argv and signal positives
require child0/parent0/backend17 twice with six reclaims. Syntax requires exit2/
backend17 twice with four reclaims. All seven corresponding rejection controls
retain exact terminal and supervisor sequences. Positive PASS markers are checked
separately. Output bytes are native owner/readback assertions, not separate host
stdout capture or independent implementations.

[Acceptance](acceptance.json), [plan](review.md), [preparation](preparation.json),
[command qualification](command-runner-qualification.json),
[connections qualification](connections-qualification.json),
[trace checks](trace-checks.json), [startup inventory](startup-cases.json) and
[artifact hashes](artifact-hashes.json) retain scope and exact identities.
All718 serial logs and available QEMU logs are retained under cases. Full local
artifacts remain in the private build root identified by preparation.json.
Producer and support packets retain verified inputs and historical failures;
large producer target archives were verified but not duplicated.

Both native suites passed on their first local attempt. Initial retention failed
because producer syntax oracles include the PASS marker while argv/signal oracles
omit it. The local terminal/reclaim sequence matched. The failed collector and
record remain retained; corrected collection compares complete lifecycle sequences
and checks marker count separately. It passed without rerunning native tests or
changing runtime inputs. Python syntax and the local quality gate pass.

Self-review checked exact source pairing, consumer bytes, owned execution,
case inventory and transcript-oracle scope. Independent technical/security/reader
review and UL-081's supported public SDK boundary remain pending. This qualifies
the private phase-one fixture; it does not upgrade newer wait/closure source sets
or count their focused evidence as full regression. Remaining work includes their
matched integration, other unchanged workloads, general signal/TTY behavior,
writable files, persistence and system assembly. Full twelve-workload acceptance,
M3, public SDK and release readiness remain open.
