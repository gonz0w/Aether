# 0017: Consume the bounded Aether native-init profile

Accepted 2026-09-05 for SI-01–03 / BG-032/BG-033/BG-040. Freeze the native-init
producer archive and retained two-ELF artifacts by the externally captured summary
hash. Write an independent sys-init supervisor, preserving producer kernel/worker
bytes and all older sys-init profiles. Kernel conformance is not consumer policy.

Accept interrupt-count deadlines and one registered lifecycle wait for this test
workload only. Do not convert ticks to production milliseconds or call it blocking
sleep. Associate channel readiness with an owned live instance, reject buffered
notification from a terminal owner, and explicitly stop independently launched
helpers. Use fresh channel/instance identity for replacement. First demonstrate
retained event observation, cancellation, expired and future deadlines, and wait
completion after target reclaim in policy-driven lifecycle sequences.

Accept opt-in fail-closed shutdown after supervisor exit/fault as a separate
outcome, not recovery. Trigger it with one live worker, one terminal worker, two
queued readiness bytes and a retained wait; require verified cleanup marker.
Retain incorrect deadline/admission policy controls and ignored-deadline/skipped-
zeroing kernel controls with exact rejection context. No production init language,
SMP, arbitrary delegation or replacement supervisor is selected. General gates
remain explicitly open. Shared standards pins and companion sources stay intact.

The ABI-6 client uses its own linker map: statically resolved GOT entries share
the immutable code page, while writable data/BSS remain forbidden. Older fixture
linker maps stay unchanged. The producer uses the same static-GOT mapping rule.
