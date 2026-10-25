# 0183: Compose an owned serial-session entry with the bounded dispatcher

Date: 2026-10-03. Before-code scope: BG-067, private AENMX009/ABI24 integration.

Consume the sealed userland wait-aware kit, preserving kernel, clients, spare
image, entropy, firmware and all other boot modules. Build a genuine sys-init
entry in this repository: validate actual boot ABI/grants, run one session through
known terminal/descriptor/pipe/backing settlement and console closure, then request
owner-authorized halt. No shell restart, profile fallback or new child authority.
Unknown/failed dispatch retains ownership and takes the existing failure path.

Reuse the sealed producer dispatcher source as an explicitly borrowed module.
Remove its fixture entry/panic handlers from the selected copy; expose only one
run-to-settlement operation and failure operation. Sys-init owns the actual entry
and final-action decision. Keep protocol, process/descriptor and cleanup mechanics
unchanged. This co-location remains part of the owner TCB and failure domain; it
is not general fault containment or a service server. The client remains userland
owned; no sibling edits or runtime adaptation are made here.

Simpler alternative: boot the delivered fixture owner unchanged. That witnesses
userland behavior but supplies no actual sys-init entry/policy. Choose a small
entry and reused dispatch rather than a rewritten runtime or delegated server.
Remove the selected module's old entry/panic path; preserve immutable originals
and historical profiles. Legacy source branches are not general product support.

Freeze source/module/linker and kit/tool hashes before compilation/composition;
read back the modified ISO payload. Inspect actual linked raw/ELF code, stack and
indirect calls before claiming acceptance. Preserve all attempts. Native positives:
immediate and35-second delayed prompt input, exact established workload streams,
identities,10 reclaims and authorized halt. Native negatives: wrong owner ABI before
admission and deliberately omitted console close causing busy halt denial without
successful halt. Preflight rejects wrong envelope/missing component identity.
Full repository checks follow final source qualification. No other-platform campaign.

Unsafe/FFI: synchronous existing int0x81 scalar/grant ABI and borrowed live buffers
remain in the dispatcher; the owned entry uses scalar halt arguments only. The
kernel validates actual holder rights; constants do not confer authority. No new
runtime dependency/ABI/resource increase;24KiB code/4088-byte stack bounds apply.
BSD-2-Clause source provenance and third-party kit notices are preserved. Existing
internal ASCII diagnostics/boot markers remain under the scoped Experience
exception. No product renderer or operator CLI is introduced.

Foundations O-01–05/I-01/03–06/E-01–08 and Distribution boot/interface boundaries
apply. This slice is private artifact composition, not a fresh kernel/client build,
maintained build recipe, full SUSTAIN acceptance, POSIX, unlimited sessions or v1
publication. Independent SDK/release review and package/storage/login stay separate.

## Candidate results and unresolved finding

The [owned candidate](../evidence/owned-serial-session-2026-10-03/README.md) boots
immediate and35-second delayed real shell workloads with exact independent
stream/identity/cleanup/halt checks. The wrong-ABI and smaller pre-admission busy
halt controls reject. Normal linked code15056 bytes, scoped stack3816/4088; one
noninlined wrapper and a larger cleanup control exceeded the stack budget and
were retained/rejected. Namespaced import and collector-prefix corrections are
recorded. The busy control tests omitted console settlement before admission,
not the initially proposed full-workload omission.

One first delayed run actually failed after the final helper, before parent
completion. Three private diagnostic reruns and the corrected normal run pass,
but no root cause is established. Therefore this is an implemented candidate with
fresh bounded witnesses, not completed integration acceptance. Diagnose that
finding before promotion or publication; preserve failed ownership/no replay.
Then finish the maintained recipe and remaining native controls. No broad runtime
refactor or generic diagnostic framework is warranted by this evidence.

The initial aggregate stops at an outdated static-record fixture count14 after
two new unsafe-boundary records were added. Updating its maintained-scope count
to16 preserves the no-tool-execution validation test. The failed aggregate is
retained; runtime/source native images are unchanged by this host-test correction.

## Further diagnosis

[Six fresh delayed cases](../evidence/serial-session-diagnosis-2026-10-03/README.md)
pass exact independent comparisons: three private diagnostic and three unchanged
normal images. Original RIP maps to the deliberate end-path ud2; its caller remains
unknown. Retained failure still rejects under the same oracle. Next instrument
direct end/panic caller paths privately; no runtime fix or completed acceptance
is claimed. Existing check-only instrumentation has incomplete failure coverage.

Further private [failure capture](../evidence/serial-session-failure-capture-2026-10-03/README.md)
now qualifies numeric check/direct-failure locations and a distinct panic marker
without widening bounds. Full capture code15984/16384, scoped stack3912/4088;
three forced failure controls and eight delayed workloads (including paced input)
pass exact semantic checks. Metadata/formatter/inspection failures are retained.
Panic caller location remains unavailable; original delayed failure still open.
Next focused reproduction using this capture; no runtime fix or promotion.
