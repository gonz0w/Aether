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

## Parent-terminal admission and settlement

The selected stronger cutpoint is the first authenticated terminal observation
recorded for parent1 by `Runtime::terminal(0)` during `poll(0)`. Before polling
indices1..3 in that same iteration, control must leave ordinary request dispatch
and enter settlement-only processing. No fresh child FILE, path/mutation, fork,
exec, stream request or new process admission may occur after that observation.
An operation already synchronously admitted before the observation keeps its
original effect/outcome obligations; this is not rollback or permission to replay.

[Issue60](https://github.com/gonz0w/Aether/issues/60) implements this cutpoint
in the actual Runtime. `run_inner` launches the parent, then its private inlined
`run_session` polls index0 first. A recorded parent terminal branches directly to
settlement before indices1..3, ordinary decoding or idle stream retirement.
One private non-inlined terminal helper keeps cleanup scratch off the active
polling call chain. No Runtime fields, extra ledger or authority were added.

Settlement reuses authenticated `stopped`, child wait abandonment and native
reclaim; the parent is reclaimed only afterward. Pending read/stream frames mean
`Completion::Pending`, whose contract guarantees no effects. Confirmed terminal
clears those slots and releases their holders. After all records settle, a final
`retire_idle([false;4])` releases idle pipe objects before checked shutdown.
Unread queued child bytes remain unadmitted; they are distinct from a partially
consumed exchange or unknown effect, which already fails and retains obligations.
Host tests exercise this production path; matched native enforcement remains
unqualified by these changes.

Do not use `gate.retire()` as graceful drain. `fork_gate::Owner::admit` requires
Idle; Retired rejects the operations that confirmed terminal handling, final
holder settlement, stream cleanup, reclaim and checked source disconnect still
need. Runtime's present error path deliberately retires the gate and retains
native obligations. That failure outcome must remain distinct from clean drain.

The implemented settlement path preserves the sole gate/ledgers and these
obligations, without a second authority table:

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

The actual Runtime tests queue child FILE write, exec, fork and stream frames
at the parent-terminal boundary. No later child byte is consumed, no reply or
provider effect occurs and no new native object is allocated. Additional cases
settle a no-effect read and reserved parent wait, require final pipe retirement,
and retain failed close/reclaim, nonterminal stop, partial exchange and unknown
mutation outcomes. Named compiling omissions restore child polling or remove
final idle retirement and must fail their specific assertions. The fixture calls
the private production session path, without a second drain state machine.

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

## Bounds and one drain deadline

Keep current root 3/home 15 rights, four service connections, 16 total handles,
4096-byte transfer/workspace limits, 96 cumulative requests and 9 cumulative
provider mutation attempts including bootstrap and teardown. Reserve request
capacity for closes and disconnect; exhausting all work slots is not clean drain.

Preserve seven domains, twelve channels, 35MiB backing, engine 8192 backing pages,
owner 128 backing pages, owner 49152 code/ 8192 resident including 4096 workspace,
8184 usable stack, engine ELF8MiB/2048 loader pages and process ELF1MiB/128 pages.
The deadline-enabled complete owner measures 49016 code bytes, 7800 resident bytes
including workspace and 8072 conservative stack bytes. This leaves 136 code bytes
and 112 static stack bytes; no native peak measurement follows. Existing writer
60s/6000 delivered ticks, reader 30s/3000 and 64KiB capture remain native qualification
ceilings. A longer interactive lifetime needs its own selected profile.

[Issue61](https://github.com/gonz0w/Aether/issues/61) selects one 500-delivered-tick
allowance for this finite drain experiment. After authenticated parent terminal,
`begin_drain` obtains one successful owner observation and checks addition before
constructing a nonzero absolute `Deadline`. It arms the sole source once through
the existing gate, before any child stop/reclaim or final FILE close. No wake,
frame, child or verifier renews that deadline. Startup and healthy-session waits
retain their existing profile; this allowance begins at the observed cutpoint.

`Control::observe_events` uses existing operation 0x2a000; `Observation::checked`
accepts only successful results before reading sequence/tick. Typed native
`park_events` passes the observed sequence in RSI and the absolute deadline in
RDX to 0x2a001, keeping selector 0xe002 and other input scalars fixed. The generic
`ctl` argument mapping is unchanged. Event, deadline (-110), cancellation (-125)
and invalid/native errors keep their existing result meanings; invalid auxiliary
registers never become a successful clock observation. `Deadline` cannot encode
zero, and zero allowance or overflow fails before source arming.

Only the source is wrapped by private `DrainIo`; its optional deadline and saved
sequence cost 16 native resident bytes. Common Endpoints, child Peers, Channel/Io,
Store/Descriptions and kernel interfaces stay unchanged. The source snapshots
owner events **before** each nonblocking transfer. On EAGAIN it parks using that
saved sequence and the original deadline, without a new observation between the
failed transfer and park. An event in that interval therefore remains visible.

The trusted `Client::configure_channel` and `ProcessFiles::configure_channel`
callbacks configure this owned transport under exclusive admission. Their
void/result interface cannot return a channel loan, and retired-source access
fails. The actual callback only arms the private adapter; it performs no RPC,
reconnection, authority change, receipt collection or mutation replay.

The same deadline passes through confirmed child stop, handle settlement,
disconnect exchange and engine-terminal/export verification. Fresh checkpoints
on progress paths and before final acceptance/reclaim/halt prevent continuously
positive transfers from evading expiry. Work counters remain independent finite
work bounds, not elapsed timers. Timeout, cancellation, partial frames and unknown
mutation/delivery outcomes fail the drain and retain obligations. Both owned
source-close attempts still occur on Client failure, even after expiry.

Known completed facts stay accurate: if engine reclaim and stale-handle proof
succeed before a later expiry check, `engine=0` records that fact while the drain
still fails and halt is forbidden. A timeout never fabricates terminal/reclaim,
clean export, block quiescence or permission to retry a mutation.

The kernel observation is an authoritative **delivered-interrupt tick** count.
It is not diagnostic UTC or a wall-clock guarantee during missing/delayed IRQs.
Kernel deadline precedence wins event ties. The whole-role wall watchdogs remain
separate. Matched native enforcement, timing and peak evidence belongs to
[issue64](https://github.com/gonz0w/Aether/issues/64); no guest is selected here.

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
logs; remove owned compiled outputs. Full native qualification of Runtime
drain/deadlines, operational reopen/provisioning, long-lived Zsh
and assembled persistent ISO acceptance remain separate from these host checks.

The simpler alternative is retaining the current finite entry and calling its
local disconnect a service lifetime. It misses the new cutpoint and settlement
obligations. Reuse the actual gate/source, synchronous ownership and existing
native stop/reclaim/park mechanisms; no new manager, daemon, ledger, runtime
dependency or authority abstraction is selected.

## Parent-terminal host checkpoint —2026-10-25 (PR63)

From the system root, the maintained component entry point is
`PYTHONOPTIMIZE=1 python3 -B sys-init/scripts/check-home-owner.py`.
At PR63 it registered nine home-owner methods and named admission/idle-retirement
omissions alongside construction, File receipt and failure controls. The deadline
checkpoint below adds its current cases to the same maintained checker.
Exact tools, SDK inputs and private formatting policy are owner-provided
prerequisites. A public checkout alone cannot replay this complete gate. Current
local measurement uses declared read-only dependency routing; private inputs and
raw receipts are never published or substituted with successful stubs.

The focused actual-runtime suite at PR63 passed nine home methods, three concrete-runtime
regressions, four internal exec regressions and both new omission controls, plus
strict host/native compilation, Clippy and Rustfmt. That checkpoint’s complete owner
linked at 47576/ 49152 code bytes, 7784/ 8192 runtime-plus-workspace bytes and 8056/ 8184
conservative stack bytes. Sources/tools were frozen, all 131 recorded commands
completed in 18.345 seconds under the 300-second aggregate and owned outputs were
removed. This is offline ELF/layout/call-graph measurement, not native peak or
execution evidence.

The first measured layout exceeded the stack ceiling by 32 bytes. Outlining only
terminal settlement reduced active poll scratch and restored fit without larger
limits. All failed attempts remain local, including initial fixture/compilation
errors and a confounded early regression attempt. The final named omission
provides the direct old-child-polling regression proof. Historical seals remain
unchanged. #56 legacy guarded coverage and #64 matched native qualification remain
separate; the next section records the implemented deadline checkpoint.

## Whole-drain deadline host checkpoint —2026-10-25

The full maintained component check body passes 911 commands in 188.399 seconds:
367 positive Rust test executions, 56 semantic controls, four host/native channel
loan denials and both host-trap guards. Strict host/native compilation, Clippy and
Rustfmt pass. Exact private input routing and compact receipts remain local;
public source alone cannot replay the complete gate. All used sources/tools were
frozen and rechecked, diagnostic bytes stayed below 4MiB, and all owned processes
and generated outputs were removed.

Actual Runtime/source framing cases cover pre-transfer event retention on EAGAIN,
repeated wakes without renewal, positive-progress expiry, child stop, final handle
settlement, disconnect and export expiry, post-reclaim bookkeeping, cancellation,
malformed/denied observations, zero/overflow, partial frames and unknown outcomes.
The Native implementation’s argument routing is exercised through a host-only
trap substitute; omitting RDX fails the named assertion. Trap selection is
rejected for non-test host and native target builds. This supplies no native
interrupt-timing witness or successful substitute syscall.

| Complete owner profile | Code bytes / 49152 | Resident+workspace / 8192 | Conservative stack / 8184 |
| --- | ---: | ---: | ---: |
| Current home | 49016 | 7800 | 8072 |
| AF07 | 43144 | 7544 | 7088 |
| AF08 | 47008 | 7640 | 7088 |

Existing actual-kernel-body controls also pass in 17.598 seconds: two positive
variants and three expected semantic negatives, with unchanged kernel sources.
All six owned commands, including pinned Zig identification, complete cleanup.
These are host executions of selected kernel bodies, not native authority or
elapsed IRQ qualification.

Failed attempts remain retained, including setup/fixture errors, the initial
stack overflow and two private kernel-harness errors. The range-guard omission
correctly triggers a named runtime integer-conversion panic; the private harness
was corrected to recognize it without weakening the maintained no-compile-error
checks. A direct Native observation call removes an unnecessary forwarding frame
and restores fixed-limit fit. No ABI, historical seal, generic transport/store
contract or resource ceiling changed. Issue 64 retains the matched native gate;
operational reopen/provisioning, Zsh/TTY and the assembled ISO remain open.
