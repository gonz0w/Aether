# UL-059 pure result decoding

The new C17 component accepts exact 32-byte admission/collection replies from the
selected two-generation command-I/O profile. It validates context, status, receipt,
error/success padding and terminal kind before publication. Wire errors -1..-4095
are converted with bounded arithmetic, without casting an out-of-range uint32 to
signed int or relying on macOS errno numbers. Collection -11 is pending; admission
-11 is an owner error. Error payloads publish no receipt. Successful collection
retains full uint32 detail and kind1 exit / kind2 fault / kind3 stop.

The terminal policy preserves normal0..255 only with explicitly complete cleanup.
Abnormal/wide/invalid facts and incomplete cleanup return1 without changing raw
facts. The policy requires a collected result; it does not map local usage or
precondition errors. Decoder failure leaves caller output unchanged. Callers must
branch on the result and cannot reuse stale output. No allocation, transport,
receipt consumption, retry, authority check or recovery occurs here. Re-decoding
bytes is not another collection; one-time consumption remains a caller/owner
lifecycle requirement. A valid format is not proof of authentic owner delivery.

The first run passes 28,159 UBSan assertions: both generations, all4095 wire errno
magnitudes, every normal0..255 status, fault/stop and wide detail, exact raw-field
copies, cleanup flags, each short length and one oversize, every success/error
padding byte, foreign receipt, invalid context/kind/status, null inputs and atomic
failure. Four mutants compile successfully and fail at exact receipt, error-padding,
terminal-kind and cleanup-status oracles. Host source mutation does not change the
owned decoded facts. This is deterministic boundary coverage, not fuzzing.

The native x86-64 relocatable object has no external imports. No new native link
or boot was run because the helper is unwired. Ordinary runner/adapter/native
drivers are unchanged. Parser1293 assertions/two mutations and21 existing command
host/control cases pass. Strict C17 diagnostics, formatting, Python3.10 grammar
(actual Python3.14.7) and the quality/three-standards gate pass. ASan remains an
open prerequisite from earlier evidence; UBSan selection was explicit.

`results/`, `parser/`, `command-host/` and `quality/` retain raw commands, logs,
artifacts and checked owned-process cleanup. Sources/plan/compiler/SDK/runtime
identities were recorded before consumption; `results/sources/` is the exact run
snapshot. `sources/` and `documents/` retain final code and progress documentation.
`owner-inputs/` retains producer command-I/O and terminal-kind documentation, checked
against the reviewed source archive's member identities. No producer source or
standard pin changed. Commands use explicit environments and30-second deadlines
(quality60), with16MiB per-output-file limits. No global performance/resource or
security claim follows. Original code is BSD-2-Clause; no new dependency adopted.

Current-task technical review by Codex checked integer bounds, validation ordering,
private lifetimes, generation scope, zero-error payloads and unchanged raw facts
through policy evaluation. Independent technical/reader and affected-owner reviews
remain pending. Foundations O/I/E, approved CE/CC/CP, TD/TC/TE and documentation
workflow apply. Any affecting input/contract/tool change invalidates evidence reuse.
Next UL-059 is native mapped-result integration, retaining receipt/kind/detail,
cleanup facts and finite-parent regressions. Public zero-admission/local outcomes,
unknown/stop recovery, ASan/fuzzing and package/sys-init acceptance remain open.
