# Process-mask host candidate (UL-067)

The [mask state](mask.c) implements the local behavior proposed in [VECTOR.md](VECTOR.md).
It is not a public/native umask replacement, launch carrier or file-creation policy.
Native CAT-04 remains NOT RUN. Original code is BSD-2-Clause; no libc or Toybox
source/pin changed.

Caller provides a private zeroed process context, an explicit initial mask0–0777
and a nonzero generation label. These must come from reviewed startup policy;
no integer or host check grants native authority. The first initialization attempt
consumes that context even when rejected. There is no implicit0077 default in the
implementation. Repeated initialization cannot overwrite a live or failed context.

A valid exchange returns the old mask and stores the requested low nine bits.
Uninitialized, retired, stale-generation and null-result calls fail without
changing state or output. Output storage must remain valid and disjoint from the
private state. Retirement clears the live mask and disables further exchange;
its history remains, so it cannot be reinitialized. A later process receives a
new context and owner-selected generation. Label uniqueness and lifetime-safe
references remain the owner's responsibility; this is not a capability table.

The same process's future threads must share state rather than silently making
thread-local copies. This candidate is synchronous and has no synchronization,
spawn/exec inheritance or concurrent reset semantics. Actual process isolation
and generation publication require native witnesses. The host tests compare two
independent state objects; they do not demonstrate kernel isolation.

No file creation is supported by the stdin-only cat candidate. Before creation
APIs are offered, the namespace owner must define application of mask and requested
mode alongside native grants. Successful local mask exchange cannot claim that
files are permission-filtered, nor does it change chmod, login or package policy.
Until accepted startup and integration exist, native umask remains unsupported.

## Tests and reproduction

```sh
python3 -B experiments/toybox-reference/check-mask.py
```

From repository root with pinned Clang21.1.8 and Python3.12+. No VM/network/native
SDK is required. The driver runs strict C17 warnings, UBSan, pinned format and
owned60-second commands in a private output root. Help/version stdout0, invalid
usage stderr64. Source/plan/tool identity and logs are retained in
[evidence](../../docs/evidence/toybox-mask-2026-09-06/summary.json).

1,048,576 scenarios cover512 initial values x512 requested low-bit values x4
high-bit patterns. Independent old-value/modulo oracles verify actual storage,
Toybox's clear/save/restore sequence, untouched second context, stale access,
retirement and fresh-context initialization. Boundary controls cover uninitialized,
invalid and repeated initialization, null APIs/output and unchanged sentinels.
Three compiled mutants return the wrong old value, retain high bits or ignore
stale exchange; each must fail an assertion. All pass their rejection oracles.

This is host state logic, not native POSIX conformance. Independent/owner review
remains pending. Next local integration: connect this state to a candidate-local
Toybox startup wrapper in a Linux reference fixture, alongside actual stdio and
shared shutdown state, with original control and distinct failure witnesses.
Do not install a global libc override or change native pins to do that experiment.
