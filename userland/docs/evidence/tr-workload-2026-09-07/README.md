# UL-013 bounded GNU tr workload baseline

One warmup and six measured invocations complete with exact expected output,
exit0,empty stderr and complete cleanup. [Summary](summary.json),
[guest results](guest.stdout), [protocol](WORKLOAD-PLAN.md). This is a successful
correctness/measurement run, not a performance acceptance result.

| Input size | Three elapsed samples (ms) | Median (ms) | Input MiB/s at median |
| --- | --- | --- | --- |
|64 KiB |15.266,16.818,17.799 |16.818 |3.72 |
|1 MiB |24.742,25.773,26.232 |25.773 |38.80 |

The measured interval surrounds the unchanged owned process helper in the Linux
AArch64 guest while QEMU executes the static x86-64 GNU9.11 candidate. It includes
QEMU startup,input/output file handling,waiting and cleanup, and excludes VM/
container startup and data construction. Rates count input bytes, not output bytes.
These are not utility-only CPU times, native throughput or provider rankings.
Helper polling and fixed overhead matter, especially for the smaller workload.
Three repetitions give no statistical confidence interval or steady-state claim.

Inputs repeat ASCII space,12345,newline to exact sizes. TR-B01 deletes the six C
whitespace bytes; expected and actual byte arrays are compared, with hashes/lengths
retained. One64 KiB warmup is separately labeled and excluded from medians. No
adaptive stopping, discarded measured sample or overhead subtraction occurred.
Clock implementation,resolution,Python/kernel,candidate/runtime/input identities
and every command record are in the report. Container absence is confirmed.

The512 MiB container and16 MiB scratch settings are configured limits, not measured
RSS. No CPU/RSS/load/parallel/native workload coverage or speed threshold was
introduced. A later candidate decision needs explicit targets and matching-layer
measurements. Reproduce with run-workload.py; changing any affecting input requires
new evidence. Previous package/subset and owner handoff scopes are unchanged.

Sources and staged inputs were reverified. [Syntax](syntax.log) and
[quality](quality.log) pass. New helpers are BSD-2-Clause; upstream terms remain.
New measurement helper review remains pending. UL-013 stays active for broader
workloads,resource metrics and native acceptance.
