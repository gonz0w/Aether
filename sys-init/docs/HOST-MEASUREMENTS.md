# Host measurement baseline

Run `python3 scripts/measure-host-runtime.py` from the repository root (or use its absolute path). Python host tooling remains experimental; this does not measure a native init, PID 1 or boot time. No production threshold or comparison with another init is asserted.

The runner verifies all three offline standards pins before spawning workloads. Each invocation creates a fresh private `out/host-measurements/run-*` directory; `--output-root PATH` selects another parent. Retain its whole directory. stdout returns a versioned JSON result/report path; progress goes to stderr. `--help` and `--version` exit 0; invalid usage exits 64; operational failure exits 1. SIGINT caught during a child check stops further work, retains an interrupted report and exits 130. An abrupt interruption outside a child wait can leave a `running` snapshot; that is not success.

## Method

Two fixed independent-service workloads: one or eight trusted Python children. Each child writes the existing READY frame and sleeps; the adapter requests ordered stop, observes terminal status and completes reclamation. Every repetition uses a fresh worker interpreter and private working directory. Each workload runs two retained warmups followed by ten measured repetitions, sequentially. Host filesystem/interpreter caches are not flushed or controlled, and unrelated workstation activity is not isolated.

perf_counter_ns measures runtime construction, request-to-observed-readiness, stop-to-observed-reclamation and total workload time. Worker imports, fixture definition and initial interpreter hashing occur before timing. Runtime construction and per-launch executable revalidation are counted as documented. The small spawned-inventory file write is included in start-to-ready time. Fixture Python startup and the adapter's five-millisecond polling interval contribute to latency.

All repetitions run with tracemalloc enabled. Memory is peak traced manager-side Python allocation since before runtime construction, in bytes. It excludes imports, interpreter RSS, native allocations not traced by Python and all child memory. CPU is getrusage user+system delta, reported separately for the manager and its reaped children. Process count is the verified live child inventory at readiness plus the worker manager; the waiting coordinator is excluded. This is not an OS-wide process census or total resident-memory measurement.

All raw samples, warmups, commands and stderr logs are retained. Summaries use median, nearest-rank p95 and maximum; with ten samples p95 equals maximum. Only successful measured samples enter summaries; failures remain recorded and prevent a passing run. A missing readiness/cleanup witness is failure. Each worker has a 20-second outer watchdog, plus finite model/fixture budgets. Deliberately silent readiness in the same worker exceeds a one-second watchdog as a negative control; it must have spawned a child first. The timeout is censored failure evidence, never a fast latency sample. Owned process-group termination cleans up this non-detaching control.

The runner is separate from `check-all.py`: performance numbers do not gate functional correctness. Its summary tests are included in the harness-evidence suite. Pinned [Distribution PF-01–PF-03](vendor/aether-distribution/v0.1.0/PERFORMANCE.md) and [Foundations E-01–E-08](vendor/aether-foundations/v0.1.0/EVIDENCE.md) govern the scope and retention. Shared pins and runtime behavior are unchanged.

## Recorded exploratory baseline — 2026-09-05

Environment: macOS-27.0-arm64-arm-64bit-Mach-O, Python 3.14.7, 18 reported logical CPUs. The CPU model and physical-memory query was denied by this environment; [host note](evidence/host-measurements-2026-09-05/host-note.json) records the missing metadata. This limits hardware reproducibility and comparison. Architecture, clock, load, executable/source hashes and configuration are in the report. There is no affinity, fixed-frequency or exclusive-host claim.

Each timing/CPU cell is median / p95 in milliseconds. Memory is median peak traced manager allocation, in KiB (1024 bytes).

| Children | Start → ready ms | Stop → reaped ms | Manager CPU ms | Child CPU ms | Traced peak KiB | Workload processes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 21.12 / 21.75 | 6.48 / 6.52 | 2.60 / 2.86 | 14.38 / 14.75 | 139.3 | 2 |
| 8 | 33.31 / 34.17 | 6.69 / 6.78 | 11.44 / 12.56 | 135.40 / 142.69 | 149.4 | 9 |

All 20 measured repetitions and four warmups passed, with zero remaining owned children. The deliberate readiness timeout was detected after child creation. [Raw results and summaries](evidence/host-measurements-2026-09-05/baseline/results.json) retain every sample and adjacent logs. These measurements support a baseline for this instrumented host experiment, not a “small and fast” production claim. In particular, child CPU includes Python fixture interpreters and cannot be read as supervisor overhead.

BG-028 retains full-process memory/size evidence, reproducible hardware metadata and production ownership choices. BG-054 retains a second-host run. Review the accumulated contracts and current native integration next; native timing needs its own declared target workload and witness.

[Functional validation](evidence/host-measurements-2026-09-05/validation/results.json) passes three standards checks, 34 model cases/three mutation controls, 38 host cases and 13 harness-evidence cases. Three new summary tests reject missing/nonfinite/negative samples and verify nearest-rank p95.

The canonical [source-checkout manual](man/sys-init-measure-host.1) documents the
current invocation, streams, failure paths and artifact lifetime. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.
