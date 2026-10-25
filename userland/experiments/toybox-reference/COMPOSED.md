# Combined Toybox reference fixture (UL-067)

The [fixture](composed.c) now runs actual standalone Toybox cat with the tested
mask, vector, session and finalizer components in one static Linux executable.
The original-object control relink remains byte-identical to the earlier cat ELF.
The candidate wraps main/umask/read/write/fflush/_exit and replaces the single
writev call in copied musl __stdio_write. All source/patch identities are retained.
This is link-time instrumentation, not the proposed native _xexit source patch,
public libc replacement or accepted child-role interface.

Before actual Toybox startup, initialize mask0077 explicitly. Observe Toybox's two
mask calls and restored value, actual upstream fflush(0), then session finalization
at terminal _exit. The fixture checks restoration and one top-level flush before
closing. Real scalar and buffered writes share vector/session state. Scalar reads
are real Linux reads capped at3 bytes; backend writes cap at2 bytes. The fixture
allows cat -e for buffered-path testing; it does not implement the proposed
stdin-only native argument admission policy.

The observer is a duplicate of Linux stderr obtained before startup. It records
bounded final facts after logical standard roles close. This extra fixture handle
is not a proposed native diagnostic grant. Close-fault injection performs a real
Linux close then reports error/unknown; it does not simulate leaked descriptors.
Unknown outcomes prohibit later callbacks; abandoned roles are ultimately reclaimed
by Linux process exit, not evidence of Aether's supervised reclaim protocol.

## Exercised cases

| Case | Exact observed result |
| --- | --- |
| Empty and binary input | Exact copy, status0; mask restored, flush observed, close order012 |
| Buffered cat -e | Exact newline-marked output and the same shutdown facts |
| Output committed then ACK lost | Exactly two output bytes, status1, poisoned state, no close callbacks |
| Input close reports error | Copy preserved, bounded cleanup diagnostic, status1, close order012 |
| Input close reports unknown | Copy preserved, status1, only input close called; remaining roles abandoned |
| Cleanup diagnostic fails | Copy preserved, no diagnostic payload, status1, close order012 |
| Invalid mask initialization | No Toybox call; empty output and observer rejection, status120 |

Every terminal path that reaches normal finalization also attempts a late public
write and requires rejection without another backend call. A compiled variant
returns the wrong old mask from umask; actual Toybox restores the wrong value and
the terminal guard exits124. This is an exercised semantic mutant, not a native
status contract. Wrong-status/trace oracle checks are retained separately.

## Reproduction and limits

```sh
python3 -B experiments/toybox-reference/check-composed.py
```

Requires existing pinned Clang21.1.8/musl Linux SDK, archive, cat objects and running
local Podman image. Python3.12+, help/version stdout0 and usage stderr64. No pull,
network or VM startup; read-only root/input, UID65534, capability drop,512MiB/32PID,
60-second owned commands and exact-name cleanup. New code uses C17 warnings and
pinned format; upstream stdio retains declared sign/unused-parameter exceptions.
Unchanged host-component UBSan evidence is reused, not Linux sanitizer coverage.

[Evidence](../../docs/evidence/toybox-composed-2026-09-06/summary.json) retains the
initial socket-denied attempt, initial eight-case pass, final full run and mutant,
all logs, source/SDK/object/patch/tool identity and ELF properties. No native runtime,
actual namespace/TTY, authority, admission, lifecycle or packaged base acceptance
follows. Independent review remains pending.

Next: consolidate the concrete native owner-review packet using these reference
results, exact missing child diagnostic/admission/lifecycle decisions and proposed
consumer patch boundaries. Keep UL-059 runner-local output separate. No sibling
message, backlog edit, source change or consumer pin update is authorized by this
fixture's success alone.
