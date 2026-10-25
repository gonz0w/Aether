# UL-013 byte-workload measurement protocol

Measure one pinned GNU tr TR-B01 workload in the current Linux/QEMU reference,
not native throughput or provider ranking. Generate deterministic finite64 KiB and
1 MiB inputs by repeating ASCII space,12345,newline. Expected output deletes only
the six C whitespace bytes, checked by exact bytes and hash. One64 KiB warmup,
then three measured invocations per size in fixed order. No adaptive stopping.

Measure guest perf_counter_ns around the unchanged owned process helper. This
includes QEMU startup, file-backed stdin/stdout, process waiting/polling and cleanup;
it excludes container/VM startup and input/expected construction. Label it owned
command elapsed time, not utility CPU time. Report every sample,median,min,max and
input MiB/elapsed; do not subtract warmup or estimate emulator overhead. Small
samples and helper polling make this unsuitable for fine latency claims.

Accuracy gate: exact output/exit0/empty stderr, complete process and container
cleanup. Operational budget:10 seconds per child,120 seconds per container,
512 MiB,32 PIDs,16 MiB private tmpfs. These are limits, not measured RSS or speed
acceptance thresholds. No performance pass/fail target is set; measurement success
only means correctness and evidence capture. No provider comparison or native gate.

Reuse SUBSET-PLAN candidate/runtime/source/tool pins and unchanged owned helpers;
read-only inputs,offline,uid65534,no capabilities. New BSD-2-Clause Python3.10+
standard-library helper. Record Python/kernel/clock identity, candidate hashes,
input/output hashes and sizes,process records, timings and cleanup. Three samples
are a reproducibility baseline, not statistical confidence. Run syntax, seven
actual cases and quality gate. Review pending. No package/native/source-trust
promotion. CPU/RSS/parallel/load/stress/native measurements remain future scopes.
