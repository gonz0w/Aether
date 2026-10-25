# UL-003/015 shared UTC plan — before implementation

2026-10-06. Aether current NATIVE-CLOCKS intake assigns UTC establishment/policy
here; raw operation0x28011 is available. Preserve v2/base bytes and elapsed waits.
Add a private opt-in reproducible runtime variant, explicit unauthenticated q35
RTC-as-UTC policy, complete mode/calendar/century validation and checked signed
seconds arithmetic. One immutable shared anchor per address-space lifetime;
initial thread establishes after runtime init and before app helpers. Readers
validate their held native grant through monotonic observation. Close after
app helpers join, before runtime finish; no adjustment/reset/realtime wait.

Forbidden: unestablished/unavailable/malformed source success, guessed century,
uptime relabelled UTC, partially changed output, silent wrapper failure, native
capability bypass or implicit public SDK promotion. One-second quantization plus
read bracket uncertainty; no authenticated accuracy/physical RTC claim.

Test Gregorian boundaries including 1900/2000/2100, BCD/binary and12h/24h,
malformed reserved/mode/source/calendars, arithmetic regression/overflow, unchanged
outputs/errno, immutable publication, helper shared reads and lifecycle denials.
Use strict C17 pinned Clang and host UBSan where available; actual native source
builds with explicit QEMU UTC dates, disabled RTC, absent policy and rejected
second establishment. Match native supervisor generations/reclaimed3 exactly.
No engine timestamp claim until actual upstream callers are rebuilt/checked.
Tool120s, guest35s/owner45s, UART1MiB/stderr4MiB, no nested tool owners, terminate/
reap without forced-kill success; full commands/source/tool pins/failed attempts.
Minimum/current Python, format, quality/standards and whitespace checks required.

Foundations O/I/E, applicable Distribution NC/PX/DS, approved TD/TC/TE and C/CP,
local SE simplicity apply. No new CLI presentation: private builder preserves
existing argparse help/version0, usage2, error1 and escaped plain streams.
Technical review is agent-scoped; reader/affected-owner acceptance pending.
Simpler alternative is explicit one-shot epoch configuration: useful but misses
new raw-source intake requirement. Reuse native clock/grant and archive replacement
instead of a daemon or second wait system. No obsolete runtime removed; v2 remains
valid for elapsed-only users. Original code BSD2; preserve musl/upstream terms.
Initial research path lookups used incorrect archive/source paths and failed before
compilation; corrected paths must be bound before use. No native attempts yet.

First builder attempt failed before compilation: adapter.h is a sealed source
member, not a runtime public header. Corrected header copy source; failed
build/utc-runtime-first remains retained.
Second precompile attempt confirmed delivery source preserves repository paths;
corrected to source/experiments/native-service-runtime. Failed second root kept.
Third attempt compiled clock/calendar, then failed missing stdatomic.h in strict
SDK. Use Clang C17 __c11 atomic builtins with explicit acquire/release orders,
as a declared compiler boundary; no new headers or base SDK changes.

Native qualification attempt1 stopped in host compilation: --no-default-config
required explicit macOS SDK include root. No VM launched. Added host-only
-isysroot; exact command and SDK path retained; next fresh attempt2.
Native attempt2 passed host UBSan but loader rejected the test ELF before entry: no TLS segment. The native ELF contract requires TLS; add a real volatile TLS probe cookie, preserving loader policy. All failed image/log receipts kept.
Attempt3 passed first two native owners, replacement rejected854. Preserve exact trace; refine test diagnostics to distinguish establishment error from pre-init/lifecycle assertions before changing the provider.
Attempt4 passes all four cases with refined diagnostics; earlier854 did not reproduce, so its exact errno is unresolved. The test previously treated kernel-permitted EAGAIN as permanent failure. Final attempt5 permits at most16 explicit establishment attempts separated by1ms native sleeps, preserves non-EAGAIN errors and tests unchanged wrappers. No internal provider retry or source success is fabricated. Earlier failure remains retained without invented attribution.
Final source review found getauxval can alter errno when the aux entry is absent, violating the positive-error UTC API contract outside the valid profile. Save/restore errno around native call. Earlier v1 packet remains immutable, superseded after a fresh build/native pass and v2 seal. Attempt5 passed all four cases and is retained separately.
Injected host-provider test first compile failed because macOS has no sys/auxv.h; use an explicit fake declaration for the injected Linux/native aux boundary. Failed root/raw command/source retained. This does not change target source or SDK. Final attempt6 native cases all pass after errno fix.

## Final technical review and completion boundary

Root agent reviewed calendar/mode/century validation, bounded epoch arithmetic,
release/acquire publication, native grant checks, initial-only admission and
join-before-close borrow lifetime. Missing aux errno defect now has an injected
regression; native rerun uses final archive. Current clock and wrapper map origins
verified exactly in all four images; source/ISO/cleanup and final seal read back.
Quality/three standards checks, C format, Python3.10.21/3.14.7 syntax and whitespace
pass. Retention preserves1951 generated identities/830 compact records before
removing279625728 allocated file-block bytes (not measured net free disk space).
No bulk archive. Other untracked/dirty repository work remains preserved.

No independent reader/affected-owner approval is invented. UL-003/015 stay active;
source trust/offset/drift and broader production schedules remain open. Aether
current real taskq worker/volume witness has progressed; exact UTC intake and
checked engine time/persistent-pool gates are now its next dependency. Wider
SESSION remains separate. This change delivers the local provider candidate,
not engine, public SDK, POSIX or release completion.
