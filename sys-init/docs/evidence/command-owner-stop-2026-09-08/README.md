# Native command stop and size simplification

2026-09-08. Seven final native cases pass under the unchanged ABI9 8192-byte code
and4096-byte stack limits. No sibling or released-standard pin changes.

The complete32/384-byte request is now borrowed until dispatch ends, rather than
copied and cleared. Every next request overwrites its full extent before dispatch;
only the32-byte extent is inspected for short requests, and384 bytes are required
before admission validation. Existing partial-frame counts and EOF checks remain.
The owner terminal is already decoded and validated by Native::observe; use its
Option directly, removing the artificial raw-syscall encoding/decoding round trip.
No native errno, terminal kind/detail, bounds or ownership check is removed.

Stop and retirement control each link at8176 bytes (16 bytes below the bound).
The prior8336-byte capacity failure remains retained separately. Measurement-only
layout files here were not booted; final native commands use the enforcing linker.
Normal generated images changed and were freshly qualified, not called identical
to the earlier accepted revision. Their final build bytes match the five-case
regression inputs. No measured peak-stack or performance claim follows.

| Case | Exact result |
| --- | --- |
| Stop | Consume and validate first complete command read, before any backend effect/reply. Actual owner terminal143/kind3, request EOF, retire both command aliases. Runner1 then backend17 in each generation; supervisor100/reclaimed6. Input unchanged, output empty, readback/EOF/stale-handle and collection/recollection checks pass. |
| Stop omission | Retain command aliases through the terminal path. The ordinary retirement check rejects1403/reclaimed0; no ordinary terminal serial lines. It does not claim recovered cleanup. |
| Positive / empty / fault | Existing exact output, terminal kinds, two generations and six reclaims all pass. |
| Wrong role / omitted close | Existing1401/1403 rejection and zero-reclaim semantics pass. |

The omission fixture uses black_box on the retained alias array only under both
stop and omission cfgs. This keeps the real terminal-state check in the compiled
control instead of allowing the compiler to specialize the rest of the protocol
around a statically known failure. It returns the identical array; no mutation
occurs in normal images. First omission variants (constant omission, second-
generation omission, opaque generation branch) failed the size assertion before
boot; their successful stop runs and failed links are retained as attempts5–7.
Final native/results.json and regressions/results.json contain the seven claimed
cases. Earlier repeated successes are not extra coverage. The first private
borrow experiment also failed type checking; its corrected sizing steps remain.

Sources and scripts accompany the raw images/envelopes and serial/build logs.
ISOs remain private; reports retain their hashes. Frozen inputs and tool identities
are those in ../init-command-intake-2026-09-08 and ../simple-service-pair-2026-09-07.
The compatible memcmp pointer-declaration warning is unchanged. No new unsafe site.

SE review: the current requirement is stop during real command exchange within
the accepted profile. The simpler alternative is to borrow the already complete
frame and use the already decoded terminal; choosing it removes redundant work
and an artificial state representation. Existing owner/protocol checks suffice;
no new journal, domain or kernel allowance is necessary. The control-only compiler
barrier is justified by the bounded executable test and has no normal-path cost.
O-04 and I-04 retain ownership until actual terminal/cleanup; I-05 keeps profile
bounds; E-01–08 keep frozen inputs and unsuccessful evidence. No new exception.

This qualifies interruption before dispatch only, not stopping an in-flight backend
effect, graceful application shutdown, sustained idle or operator poweroff. The
frozen handoff explicitly leaves watchdog/wait and authorized final shutdown open.
Full local checks and final integrity verification are recorded below.

Final validation: all ten local gates pass in run-7r_l6q9j with checked sources
unchanged. Final source matches the staged build; regression images match final
normal builds, tool hashes and all three released locks remain fixed.
`git diff --check` passes. Seven final native cases pass; failed attempts remain
retained. This is not independent review or sustained-boot acceptance.
