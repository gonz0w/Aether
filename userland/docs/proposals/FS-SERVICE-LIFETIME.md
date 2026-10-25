# Boot-session filesystem lifetime — UL-082

[Issue 9](https://github.com/gonz0w/Aether/issues/9) owns live scope, review and
continuation. This contract selects one bounded boot-session lifetime toward the
persistent Zsh ISO. It does not select a daemon beyond its authenticated parent,
restart/recovery, installed home/login policy, existing-home reopen, new ABI,
clock trust or larger resource limits. Native execution needs a later exact
owner disposition. [PROJECT](../../../PROJECT.md), component responsibilities and
[public input availability](../../../docs/PUBLIC-SOURCE.md) remain binding.

The selected behavior is one engine, one authoritative filesystem `Owner`/backend
and one source connection across two client work phases separated by a controlled
no-request idle boundary. Parent termination closes admission, then settlement,
checked disconnect, export proof, block quiescence and native reclaim finish the
same lifetime. A phase boundary never resets counters, recreates the Owner,
reconnects its source or grants fresh authority.

## Executable and producer/consumer selection

The current source foundation is the explicit AF09 composition described by
[FS-HOME-PREP](FS-HOME-PREP.md), not an installed filesystem-service package:

| Role | Existing source and artifact | Authority and selection |
| --- | --- | --- |
| Engine, native slot0 | `launch-home-owner.rs` main, `native-home.rs` callback and original C importer/provider; guarded `filesystem.elf` | `aether_fs_home_engine_run` retains the one SPA/import/backend through callbacks and ordered export. Existing entry grants include delegated region `0xf101` and authenticated request-reader/reply-writer bootstrap tokens. |
| Boot owner, native slot6 | sys-init `owner_entry.rs`, `owner_runtime.rs`, matched `owner.elf`/`owner.bin` | Sole process/FILE/stream owner; native factory, observation/park, console and halt grants retain their existing meanings. It provisions engine0 and starts parent1 only after source construction. |
| Source/client | Actual service `Owner`, `service::run_home` and `Client::connect_home`; sys-init `Runtime::connect_home_in_place` | AFSRPC09, epoch-bound root token1/right3 and home token2/right15. Paths, labels1000/1000, PIDs and copied handles are not authority. |
| Parent and helpers | Existing guarded shell/helper process ELFs in AENFS005/AENMX010, ABI31 | Parent1 owns the bounded session; existing child slots and authenticated native generations remain fixed. Package installation does not activate this lifetime. |

The host lifetime test selects current `fs_namespace`, `fs_lifetimes`, `fs_mixed`,
`fs_wait`, `fs_bulk`, `fs_runtime`, `fs_activation`, `fs_names`, `fs_directories`,
`fs_metadata`, `fs_directory_contexts`, `fs_home`, `fs_home_wire`,
`fs_home_activation` and `fs_home_native` library code. The last selection keeps
96 total service requests and 9 total mutation attempts even with `fs_runtime`.
Do not accidentally select the unlimited generic runtime counters.

The native `fs_home_probe_three` workload and fixed UTC window remain their exact
diagnostic profile. The host experiment's two bootstrap mutations plus two writes
are 4 attempts; it cannot satisfy that native profile's exact 3 predicate. A later
matched native workload/selection must name its exact operations and count before
building. Neither this contract nor a host pass changes that predicate, the
fixed clock, an old seal, default profile or immutable helper bytes.

## Start, readiness and client admission

The existing `native-home.rs::bootstrap` attaches an administrative source,
creates `home`, validates its live non-root directory handle, creates `probe`,
verifies the empty file and closes its temporary probe handle. It retains the
original and normalized bootstrap outcomes. Provisioning failure, uncertainty or
clock rejection does not publish readiness or retry. Existing-home reopen and
installed provisioning remain separate work.

`Owner::attach_home` creates both recipient grants in the existing handle/session
ledger before publication. `home-activation.rs` validates the first greeting and
publishes native readiness once before sending it: a 64-byte greeting cannot fit
in the 32-byte native queue until the dependent runs. This is prepared attachment,
not completed greeting transfer. The client admits filesystem work only after
both complete greetings validate epoch, token, kind and reserved fields. Report
`ready` becomes true only after both sends; retained readiness never substitutes
for current native liveness or a new generation.

No user request chooses the administrative source, grants, epoch or SPA. One
source/gate owns the process binding and shared open-description state. The two
work phases retain the same connection, home grant, file binding and mutation
history. Idle means the host fixture reaches a receive boundary with no submitted
request; it does not prove native event parking, elapsed idle time or a new timer.
The native owner already observes then parks when a poll cycle makes no progress.

## Required drain cutpoint and current implementation gap

The selected stronger cutpoint is the first authenticated terminal observation
recorded for parent1 by `Runtime::terminal(0)` during `poll(0)`. Before polling
indices1..3 in that same iteration, control must leave ordinary request dispatch
and enter settlement-only processing. No fresh child FILE, path/mutation, fork,
exec, stream request or new process admission may occur after that observation.
An operation already synchronously admitted before the observation keeps its
original effect/outcome obligations; this is not rollback or permission to replay.

This cutpoint is **required and unimplemented**; [issue60](https://github.com/gonz0w/Aether/issues/60) owns implementation. Current `run_inner` polls all
indices0..3, calls stream `retire_idle`, then checks the parent's terminal field.
Thus a child's ordinary request can still be dispatched after parent terminal was
observed earlier in that iteration. The host tests below do not qualify this
Runtime boundary. Moving only the final `if` is insufficient unless required
settlement remains possible and is tested.

Do not use `gate.retire()` as graceful drain. `fork_gate::Owner::admit` requires
Idle; Retired rejects the operations that confirmed terminal handling, final
holder settlement, stream cleanup, reclaim and checked source disconnect still
need. Runtime's present error path deliberately retires the gate and retains
native obligations. That failure outcome must remain distinct from clean drain.

The bounded next runtime slice must preserve the current sole gate/ledgers and
provide this settlement-only path, without a second authority table:

1. Observe authenticated parent terminal; stop ordinary decoding/admission before
   any subsequent child poll can admit work. Only the existing authenticated terminal encodings are accepted: normal
   exit (`kind1`, status1..256) or confirmed stop (`kind3`, status144). Other
   fault/terminal encodings fail explicitly; they cannot become graceful drain.
2. Preserve in-flight FILE delivery, retained mutation receipts, partial frames,
   pending stream ownership and admitted child/copy/exec handshake obligations.
   Do not fabricate a delivered reply to a dead parent. Incomplete or unknown
   delivery is a retained failure, not successful teardown.
3. Observe or stop already-admitted children through existing `stopped` semantics;
   require confirmed terminal before reclaim. Use the existing child-ledger
   `abandon_after_parent_terminal` rule for undeliverable parent wait receipts.
   Only after native reclaim settles each authenticated process view may the
   final aliases/holders and retained CWD/source handles be released.
4. Keep terminal/holder/stream settlement callable while ordinary admission is
   closed. Any gate failure must retain the unresolved obligations and prevent
   a clean source/export/quiescence claim.

The first follow-up must test parent-terminal plus a queued child FILE write,
fork/exec or stream request in one poll cycle; no request may reach its provider
or allocate after the cutpoint. It must also test existing pending work/children
settling successfully, failed close/reclaim and unknown mutation completion,
with no forged success from irreversible failure retirement.

## Checked shutdown, export and quiescence

`ProcessFiles::disconnect_checked` already rejects live process views as Busy.
After every view is settled, it delegates to the one Client's checked disconnect.
The Client validates the disconnect acknowledgment, runs the exclusive verifier
before closing either local endpoint, and closes each endpoint once even when
verification fails. Ordinary Client `disconnect` or local `Drop` alone does not
prove native export, block quiescence or process reclaim.

Current Runtime has four process records (parent1 and child slots2..4); this
contract expands neither that ledger nor the seven-domain native limit.

Current Runtime shutdown supplies the native verifier: observe engine terminal,
require the expected successful normal status, require reply EOF and request-side
`-32`, retain actual source close results and require both zero. It then reclaims
the engine and confirms its native handle is stale, closes the console, and asks
for authorized halt. The kernel halt boundary rejects admitted workers, live
channel holders/bytes or an unclosed block device. Readiness, reply acceptance,
backend Drop, clean ordered export, native stop/reclaim and block quiescence stay
separate facts. Original engine/C teardown remains responsible for ordered export
and block drain; no host Backend destructor models those operations.

Preserve committed/partial/unknown mutation outcomes and attempted offsets until
their owning operation's receipt is collected. Reply loss, uncertain provider
progress, failed verification, nonzero local close, failed reclaim or unknown
stop prevents clean acceptance. Do not retry a mutation, reconnect, reset a
counter or reinterpret a retained failure receipt as clean shutdown.

## Bounds and elapsed deadline gap

Keep current root 3/home 15 rights, four service connections,16 total handles,
4096-byte transfer/workspace limits,96 cumulative requests and9 cumulative
provider mutation attempts including bootstrap and teardown. Caller selection
must reserve request capacity for closes and disconnect; consuming all 96 work
requests and then asking for disconnect is exhaustion, not clean drain.

Preserve seven domains, twelve channels,35MiB backing, engine 8192 backing pages,
owner 128 backing pages, owner 49152 code/8192 resident including 4096 workspace,
8184 usable stack, engine ELF8MiB/2048 loader pages and process ELF1MiB/128 pages.
Current measured owner 8160 conservative stack leaves 24 bytes; no spare capacity
or native peak-stack result follows. Existing writer 60s/6000 delivered ticks,
reader 30s/3000 and 64KiB capture remain native qualification ceilings; no guest is
selected here. An interactive lifetime beyond those diagnostic limits is not
silently authorized by the phrase boot session.

Runtime's `remaining` is a finite work allowance consumed by polls/transfers;
it is **not elapsed time**. `Control::ctl` currently passes its third scalar in
RSI and fixes RDX at zero. The kernel's existing `0x2a001` event-park operation
accepts an optional absolute tick deadline in RDX; the current owner adapter
therefore selects no deadline. A later typed adapter must carry the existing
observed sequence and explicit deadline, preserve event-before-park and terminal
races, distinguish deadline/event results and fail rather than restarting its
budget. [Issue61](https://github.com/gonz0w/Aether/issues/61) owns this typed adapter; it does not select a new timer, larger limits or a
claim that a work counter bounds elapsed drain. Until implemented and checked,
finite elapsed drain and the stronger admission cutpoint remain open coverage.

## Focused current-code host proof

[service-lifetime-tests.rs](../../experiments/filesystem-service/service-lifetime-tests.rs)
links the actual current metadata, policy, service, client and activation crates.
Its storage and channel implementations are host substitutes; no parallel owner
state machine, SPA import, kernel control call, native timing or durable export
is simulated as successful OS behavior.

The selected proof keeps one actual Owner/backend and client across a write/read
phase, a controlled no-request receive boundary and a second write/read phase,
then one checked disconnect. It asserts one root acquisition/publication/backend
Drop, unchanged home grant, global 7 requests including close/disconnect and 4
mutations including bootstrap. Controls cover root write denial, malformed home
greeting, lost/committed/completed-error second-phase outcomes without replay, the nine-attempt
aggregate limit, verifier failure versus raw close success, and exhaustion of all
96 requests without a teardown slot.

Build as a host Rust 1.98.0/edition 2021 test crate against these five public source
crates, using the flags above, `-Dwarnings -Dunsafe_op_in_unsafe_fn`, and unsafe
forbidden for the lifetime test and safe policy/service/client/activation crates.
The metadata FFI crate retains its existing audited unsafe allowance. Supply each
named crate with explicit `--extern`/`-Ldependency` paths from an owned host work
directory; `rustc --test service-lifetime-tests.rs` then runs with
`--test-threads=1`. The private compact experiment receipt retains the complete
argument arrays, source/tool hashes and outcomes. Exact pinned tool inputs are
owner-provided prerequisites; no SDK, source tree or runtime artifact is copied.
The lead owns workflow/quality registration and separate review before integration.

Use one 300-second host aggregate, each leaf at most180 seconds, bounded4MiB
streams and the existing owned-process helper. Keep failed attempts and short
logs; remove owned compiled outputs. Full native qualification, stronger Runtime
drain, typed elapsed deadlines, operational reopen/provisioning, long-lived Zsh
and assembled persistent ISO acceptance remain separate from these host checks.

The simpler alternative is retaining the current finite entry and calling its
local disconnect a service lifetime. It misses the new cutpoint and settlement
obligations. Reuse the actual gate/source, synchronous ownership and existing
native stop/reclaim/park mechanisms; no new manager, daemon, ledger, runtime
dependency or authority abstraction is selected.
