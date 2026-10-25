# UL-007/081/082 stream aliases and observed final close

Pre-code scope: extend the same tagged-table implementation with mixed dup/flags/
close. Existing file-only helpers/contracts stay callable and exact predecessor
candidate bytes immutable. Mixed file entries delegate to them. Console/pipe dup
creates a logical alias to the same owner-issued binding, not another native grant;
flags are per-logical-FD client state, not proof of native exec. Last alias requires
actual close adapter; nonlast close only removes local alias. Alias identity is
kind AND selector, so file3 cannot keep pipe3 alive.

Trusted stream close returns {complete,consumed,status}. Complete1/consumed1/status0
is observed success; complete1/consumed1/negative errno is terminal close error and
clears entry while returning error. Complete1/consumed0/negative errno preserves
entry. Unknown/invalid combinations retire file admission and preserve metadata,
never retry or infer native stream cleanup. Successful unconsumed close is invalid,
not a successful no-op. Missing last-close adapter=-38. Source status must be0 or
negative signed32-range private errno. Owner retains actual endpoint/process/
quiescence evidence and cleanup for unknown stream state. No new wire/profile.

Reuse decoded canonical map with exclusive/nonreentrant access and existing
ready/free/lookup helpers; no extra users[] ledger or service policy. Existing
source rights/ref/generation/lifetime must be reconciled externally. Native fork/
failed exec/immutable admission and full startup selection remain unimplemented.
Flags must not trigger destructive cleanup before successful real image admission.

Host tests: real OS pipes exercise read/last close and independently observed FD
lifetime; controlled results cover known unconsumed/consumed errors, unknown with
both actual states, invalid results, missing callback, capacity/stale/bounds and
console aliases. Synthetic file-endpoint callbacks isolate stream tests; this is
not native Aether streams. Every C child first runs14 stream scenarios, then its
existing269-case real C/Rust file transcript through mixed file delegation. Build
fixture object with explicit symbol aliases and separate wrapper object, preserving
pinned predecessor fixture source. Actual C child/source thread/owned group cleanup.

Pin table18/routing16/bindings6/facade12/client9/wire20/service77 and exact compiler/
formatter/libraries/resource/SDK/runtime/helper before consuming. C17 strict/UBSan/
format and unchanged Rust2021/default Clippy/rustfmt/unsafe checks. Minimum/current
Python;60s compile/30s suite/16MiB streams/clean owned roots. Specific compiling
omissions must fail semantic assertions and observed failed C child. Retain all
attempts, local quality/syntax/whitespace and canonical follow-ons.

Simpler alternative: add startup_users[] or always close source per local close.
The former duplicates the map's state; the latter breaks surviving aliases. Scan
sixteen existing slots with kind/selector identity and explicit close observation.
Reuse existing source/file policy; no generic transaction/async framework. No old
accepted path removed now; actual shell selection must replace legacy table policy.
Independent owner/reader and full UL/M3/R1/native gates remain open.

## Implementing-agent technical review and results

Reviewed lookup/ready refactor, kind+selector alias scan, local capacity preflight,
per-logical flag update, explicit final-close observation and file delegation.
No additional live counter/table, authority, dependency or native profile. Code
uses existing bounds and client fail-stop; known consumed error clears exactly
one entry, unknown retains occupancy and denies source replay. Callback truth,
source rights/lifetimes/deadlines/cleanup remain trusted external prerequisites.
No destructive exec operation is added. This is implementing-agent review only;
independent consuming-owner and reader review remain pending, not fabricated.

Actual Python3.10.21 and3.14.7 each pass269 live file cases, fourteen host stream
scenarios per child and six compiling assertion-specific controls. Strict C17
warnings/format/UBSan, Rust2021/default Clippy/rustfmt/unsafe checks pass. Exact
107-header SDK closure and resource/runtime/source pins recheck. The first run
passed the baseline and caught skip-terminal-clear at the earlier successful
final-close assertion on slot4; the checker had expected the later terminal-error
assertion on slot3. Corrected the diagnostic oracle only, preserved that failed
attempt, then current plus final minimum/current runs pass. Production bytes did
not change to accommodate the control. Every owned attempt is retained.

No native execution/link/fit claim, pipe creation/write or actual console adapter.
Next: consuming-owner startup/source reconciliation and actual native adapters,
selected shell/table/profile, native copy/failed-exec preservation, immutable image
admission and complete dispatcher/fit/fresh native qualification. Full UL/M3/R1
and packages/Zsh/TTY remain open. PROJECT intent and all immutable prior packets,
release pins, machine markers, source limits and sibling trees remain unchanged.
