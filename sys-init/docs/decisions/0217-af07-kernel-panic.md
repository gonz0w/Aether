# 0217: Preserve the actual ABI31 kernel panic and identify its supplied caller

2026-10-23 / BG-070. Root [pre-code review](../../../docs/reviews/2026-10-23-af07-kernel-panic.md)
records requirement, forbidden outcomes, security/simplicity, bounds and test
selection. Root STATE owns integration; [compact results](../../../docs/evidence/af07-owner-native-2026-10-23/README.md)
preserve all attempts, approvals, preparation and check hashes.

The approved framing sequence passed pristine original-file/media checks, then
writer hit `AETHER PANIC: reached unreachable code`. Both VM stops confirmed;
no recovery/retry or confirmed engine export/reclaim. Retained tail has helper2/
owner6 waits but no established helper/parent/engine terminal. Old panic hook
ignored its return-address argument; exception capture lost full transcript and
exact stopped media. Cause and metadata effects unknown. Do not guess a runtime
fix, hide the assertion or claim attempt2's framing attribution explains this.

Selected ABI31 alone now emits its supplied non-null caller PC before the exact
existing panic line, using fixed64-byte scratch. No unwinder, pointer dereference,
heap, capability or unsafe authority change. Old/null output exact. Pinned Zig0.16
FullPanic.reachedUnreachable supplies @returnAddress; retain PC and map PC-1 as a
candidate caller location against the exact frozen executable PT_LOAD range.

Qualifier failure capture now preserves the same bounded non-clock transcript as
success, including panic/EOF/watchdog. Confirmed stop permits stopped-media snapshot
and lookup; unknown stop preserves resources. NativeStopError takes priority even
if report writing fails. Symbol lookup failures retain the original guest error.
Prepare keeps only two pending ISOs, one exact hashed writer kernel ELF and receipt;
ELF and pinned LLVM21.1.8 symbolizer join the freeze. No VM in preparation. Confirmed
stop/lookup disposes binaries/media; compact results remain, never full archives.

Offline symbolization disables debuginfod, checks ELF/tool identity and executable
PC bounds, rejects malformed/multiple sites and records missing/unresolved evidence.
Existing host-tool bounds:10s and4MiB combined output, at most4096 retained mapping
bytes plus warning count/hash/1500-character prefix. Initial4096-byte combined cap
failed on repeated LLVM premature-aranges-terminator warnings; preserve that failed
host test. Actual controlled source/ELF lookup passes under the existing tool cap.
Warnings remain explicit; locations require source/instruction verification and
are not automatic root-cause attribution.

Actual selected/old/null panic and compiling omission plus tick checks pass;
eleven component methods cover intake/oracles, failure capture/reap, unknown-stop
report I/O, exact real host ELF lookup and PC/tool/ELF denials. Root results record
the broad checkpoint, environment limitations and targeted completion. Fresh
engine v8/activation v4/guarded v3 do not rewrite old seals or released pins.
Owner code39376/49152, resident7504/8192, conservative stack8000/8184 unchanged.
Same writer60s6000/readers30s3000,35MiB/seven domains/twelve channels,64KiB transcript,
fixed script/zero FS mutation requests, separate9/96 qualification. Import/export
may write metadata. New one-sequence diagnostic disposition is required; no VM
retry so far. Stop first unexpected result, no recovery without strict writer
success. A pass without recurrence does not resolve the unknown panic or authorize
resumed affected acceptance. Public CWD/persistent bindings/packages/Zsh/ISO remain.
