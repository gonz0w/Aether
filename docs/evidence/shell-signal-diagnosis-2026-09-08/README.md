# Intermittent signal entry diagnosis

Requirement: identify the preserved terminal-75 failure without weakening any
entry, mask, register or return checks. First amplify the existing loop in an
isolated diagnostic fixture, keeping kernel sources unchanged. Use current split
statuses and exact native logs; a passing retry does not clear the issue. Retain
all attempts, sources and build commands. No sibling, ABI, grant or quota changes.

Diagnosis: forced yields reproduce terminal 82. Temporary kernel logging captures
entry flags 0x10293 (RF set), with valid user selectors, RIP/RSP and MXCSR. The
same decoder used for hostile user returns rejects RF in the trusted trap image.
Fix scope: clear RF in the kernel-owned entry payload before strict decoding;
do not relax user-return validation or ordinary scheduler restoration. Add a host
entry/return distinction test and an amplified native yield fixture. No new API,
state, grant or quota. RF is transient debug-resume state; debug delivery is not
implemented. Intel SDM Vol. 3B describes RF management around interrupts and IRETQ:
https://cdrdv2-public.intel.com/671427/253669-sdm-vol-3b.pdf

Selected qualification: full command-runner, default regression and host suites;
a host counterexample removing normalization must fail. No failure retry is
accepted as a fix. Remove temporary kernel logging and retain its source/logs.

## Attempt inventory

- `signal-loop-diagnostic`: packaging error, rejected before native admission;
  corrected entropy extent is 48 bytes, after the 32-byte envelope header.
- `signal-loop-diagnostic-2`: 1,000 iterations/generation pass, unchanged kernel.
- `signal-loop-diagnostic-3`: 10,000 iterations/generation pass, unchanged kernel.
- `signal-loop-diagnostic-yield`: same scale plus yields before entry and inside
  handler; fails terminal 82/owner 1501, unchanged kernel.
- `signal-loop-diagnostic-kernel`: temporary logging reproduces terminal 82 and
  records RF. Source before/after logging retained here; no logging remains.
- `signal-loop-corrected`: the same yield payload passes with normalization.
- `signal-rf-mutant`: removing normalization fails the specific host test.
- First M4 regression cannot bind its local QMP socket under the sandbox. The
  authorized rerun passes all seven cases. Both directories/logs are retained.

Diagnostic user sources and compile/link/build argv are retained in their target
directories. Prior kernel sources are in the unchanged permissions packet;
`native_c-before.zig` matches that snapshot, and `native_c-diagnostic.zig` is the
only temporary logging delta. Diagnostic build flags do not expand quotas.

## Qualified results

All 238 command cases and seven M4 cases pass (245 target cases). The amplified
native case completes two generations/four reclaims. Host checks include 98 Python
tests and all offline pins; nine codec tests pass in ReleaseSafe. The normalization
removal mutant fails at the intended test. Formatting, syntax and workflow pass.
Runtime changes are limited to native_signal.zig, startup-client.c and the existing
launch harness. The original combined terminal 75 has no detailed telemetry;
this reproduction proves an RF rejection on that path and its correction, without
claiming retrospective certainty about the original predicate. No full dash,
independent consumer acceptance, debug API or broad stability certification.
