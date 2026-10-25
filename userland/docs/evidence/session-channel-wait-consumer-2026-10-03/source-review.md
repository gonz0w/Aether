# Technical source review — UL-007 / UL-081

Reviewer: Codex implementation agent, 2026-10-03. This is a scoped technical
review; independent reader identity/disposition remains pending (SSDK-06 deferred).

Reviewed runtime.c selection and startup, channel-transfer.h, the exact derived
wait-transport.h delta, vendor startup-adapter.h mask/FD paths, and current
component/rebuild/lab admission. Frozen vendor transport SHA256 d4796885…cbbd and
all provenance entries remain exact. The derived transport preserves upstream
style; the new transfer/control files use the pinned local Clang-format profile.

The wait path is selected only with SESSION_SERIAL. Native adapter supplies r8/r9
zero; wait explicitly supplies all other reserved arguments zero and the same
reader/writer endpoint used by the attempted transfer. No native rights are added.
Offset moves only on 1..request progress; request is min(remaining,16). Readiness
adds no bytes and does not change the buffer pointer. Zero/negative/oversized
transfers or nonzero wait poison before another transaction. Even a positive
invalid wait result fails. No partial-prefix replay or fallback from ENOSYS.

All synchronous public FD operations retain startup_mask_enter/leave around
exchange. An unexpected EINTR outside that mask is treated as protocol failure;
it is neither dequeued nor delivered/restarted by this loop. The existing poisoned
exit path skips close transactions; native owner drain/confirmed terminal/reclaim
remains authoritative. Host cases exercise failure suppression; native injection
of userland wait-EINTR, all unmasked interactive signal schedules and native
writer-backpressure coverage for this client remain follow-ons. Kernel mechanism
qualification remains the separately sealed producer packet.

The loop has fixed scalar state and no allocation or retained pointers. Healthy
idle waits at the enforcing kernel boundary rather than consuming an arbitrary
iteration budget. This does not promise cancellation, timeout, unlimited child
lifetimes or all scheduling/fairness behavior. Native outer deadlines, bounded
serial/log files and inherited emulator process group provide experiment bounds.

Builder profiles are explicitly selected and bound to both runtime compile steps.
Receipt admission defaults to008, with009 requiring matching explicit selection.
Sealed support loading and unchanged process helper preserve cached-module
isolation and checked cleanup. The trusted recipe remains executable build code,
not a hostile-code sandbox. Lab input profile matches envelope and SDK profile;
all actual ISO boot modules must match the pinned input inventory before a kit is
published. No kernel/owner/source edits in sibling repositories.

Host28 transfer cases (plain/UBSan), five semantically rejecting mutants,
minimum/current interpreter profile denials and rebuilds, and native exact
byte/lifecycle oracles support these scoped findings. Whole default ABI23 ELF
hashes remain identical. ASan remains unavailable on the previously diagnosed
Clang21/macOS host; UBSan and native isolation are the selected compensation,
not an ASan waiver or release certification. Shared pins and marker bytes unchanged.
