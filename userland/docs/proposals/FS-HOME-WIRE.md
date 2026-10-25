# Home service/client binding — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested service/client integration after the completed
[home delegation library](FS-HOME.md). This record owns that distinct bounded
outcome through root [STATE](../../../.planning/STATE.md#system-work-index).
Owner: userland filesystem implementing agent. Base
`854d40be840d57c86ecee99c7bda1dd4f5e426f3` on `codex/consolidate-system`;
candidate `codex/fs-home-wire`, target that unchanged consolidation branch.
Apply root PROJECT, pinned METHOD, DEVELOPMENT and userland quality PROCESS.

Finite outcome: actual service/client interoperability for one authenticated
connection with read-only system root and writable home, using the existing owner
delegation and tables. Add explicit `fs_home_wire`/AFSRPC09 selection, two-grant
greeting and client binding. Preserve existing AF01–08/default consumers. This is
host/synthetic-storage and no_std library qualification; native admission remains
a separate gate.

Non-goals: home creation/layout, native ready publication, activation/loader ABI,
client mutation APIs, process CWD or FILE/libc writes, login/admin policy, new
channels/workers/heap/resource limits, executable fit, guest execution, SDK/pin
promotion or persistent Zsh/package/ISO acceptance. The existing service mutation
wire is exercised directly by hostile/authorized test clients to verify enforcing
authority; this does not claim a public Rust write API or POSIX write semantics.

## Contract before implementation

For the service, `fs_home_wire` requires `fs_home` and its existing directory-context prerequisites.
The trusted `run_home(owner, channel, source_peer, source_session, home, peer,
epoch)` consumes one Owner/channel. It calls `attach_home` with the exact source
handle before output. Failed provisioning sends no greeting, dispatches no request,
shuts down Owner and attempts both channel closes. No incoming request chooses
source authority, endpoint peer or service epoch. Epoch must be nonzero/nonreused.

AFSRPC09 is a deliberate incompatible selection. Send two ordinary64-byte entry
frames: status0/epoch/token1/kindDirectory/root size/zero bytes48–63, then the same
shape with token2/home size. Their positions mean root rights3 and home rights15;
neither frame contains native handles, backend IDs or credentials. The server
binds those exact delegated handles to tokens1/2; subsequent tokens begin3 and
never reuse. `Report.ready` becomes true only after both frames transfer. Failure
of either greeting stops without dispatch/replay. Transport greeting completion
does not authenticate endpoints or publish supervisor readiness.

Reuse the existing names/bulk dispatch loop and its complete-body validation,
request/mutation limits, error receipts, retirement and cleanup. Extract only its
provisioning/greeting seam; do not clone the whole dispatcher. Old `run` continues
its old one-root behavior on old selections; it is unavailable for AFSRPC09. Existing
activation consumers reject the new selection before native use.

`Client::connect_home(channel, epoch)` requires the matched service selection.
Validate both greetings completely before publishing either binding or returning
Self. Invalid provisioning, wrong magic/epoch/token/type/reserved bytes, error or
loss consumes both local close obligations exactly once and yields ConnectFailure.
Root/home occupy existing slots0/1 with fixed rights3/15; next token3. `home()`
returns only that retained live binding. Root and provisioned home cannot be closed
individually; disconnect/abort/drop keep their existing once-only behavior. No
Client field, allocation, counter reset or extra channel is added.

Old `connect` and in-place read-only constructor refuse a home-selected client
before receiving input. Compile-time client selection and the existing exported service MAGIC reject
mismatched dependency selections, including sealed AF07 producers without a
HOME_GRANTS symbol. Existing remote description/FILE and activation
consumers explicitly reject home dependencies until their own contracts integrate
them. No fallback or peer-driven negotiation.

Existing client lookup/read/stat/parent/path calls operate on the two retained
bindings. Lookup rights remain attenuated; READ aliases through root cannot
recover home mutation rights. Parents always receive read rights. The service
still enforces denied raw writes/mutations, even if local checks are bypassed.
No process initial CWD is chosen here. Exclusive mutable access serializes client
operations; malformed/partial responses retire without replay.

## Security, resources, simplicity and tests

Apply pinned O-01–05/I-01–08/E-01–08 and adopted CE/CD/CR/CA/TD/SE requirements.
Trusted Owner/backend and authenticated endpoint provisioning remain in the TCB.
Untrusted headers, token labels, name/data bodies and partial transport must never
select provisioning authority, elevate root, publish half a client, or reuse a
retired connection. Keep16 bindings/handles and current connection/request/data
limits; home permanently consumes a second slot. Source provisioning remains in the owner ledger until consumed Owner shutdown.
In the tested source root/home-pair configuration, the source plus two recipient
grants leave12 free owner handles versus14 free recipient token/client slots.
Additional preexisting handles reduce that capacity. Owner Full must not advance tokens. Native
cleanup/lifetime fit remains unqualified.
No new unsafe/FFI/assembly/dependency. Existing fixture Rust2021 and pinned1.98
format/compiler conventions are retained; no unrelated style migration.

Simpler alternative: reuse the single-root greeting and change its meaning.
Insufficient: it would hide the second grant and silently widen old consumers.
Choose two checked existing entry frames and one shared dispatcher seam. This
borrows existing explicit token/rights attenuation; it adds no VFS, second SPA or
policy service. No compatibility path is removable while frozen consumers use it.

Write interoperability/failure tests before code and retain the actual red result.
Test actual owner/service/client home and root reads, exact rights/token sequencing,
physical home/parent paths, local attenuation and server-enforced root denial;
raw home create/write versus root/alias denial; wrong provisioning; both greeting
losses and every malformed identity/type/reserved field; cleanup once, no dispatch,
no replay; capacity, foreign tokens, stale handles, malformed padded bodies and
reply loss. Compile semantic omissions for missing second greeting validation,
wrong root/home token binding, widened root rights and premature readiness as
applicable. Keep affected old service/client regressions and both host/no_std
selected/AF08/AF07 builds; test mismatch and old-consumer compile rejections.
Measure Client/Owner layout without claiming complete executable fit.

Command from `userland/`, registered before execution:
`python3 -B experiments/filesystem-service/check-home-wire.py`.
Use pinned existing owned-process helper, private build root,300-second suite
deadline, bounded children, frozen tool/source hashes and compact all-attempt
evidence with generated-output cleanup. CLI follows the existing home checker:
stdout help/version/JSON, escaped stderr,0/1/2/64 exits. Run relevant standards,
workflow/userland-quality/link checks and separate peer review before integration.

## Status and continuation

The pre-code contract and eight tests preceded implementation. Actual missing-API
compiler red is retained; no semantic runtime test-first claim. Final
[evidence](../evidence/filesystem-home-wire-2026-10-24/README.md) maps each criterion
to observed outcomes and retains all seven attempts. Attempt07 passes135 child
checks under PYTHONOPTIMIZE=1: eight new interoperability tests,65 affected host
regression executions, six compiling semantic controls, strict Rust checks,
selected/old/sealed host and no_std builds, consumer/mismatch/prerequisite rejection
and unchanged680/8 Client layout. Native execution/fit is untested. Owner layout
evidence is reused from unchanged FS-HOME; no Owner/Client/Binding fields were added.

Peer source review found a checker optimization defect: Python assert statements
could disappear under -O. Explicit require checks now preserve every oracle;
the optimized final run and dedicated CLI control pass. The source-slot capacity
claim is scoped to the tested source root/home pair. All sources/tools/pinned
libraries verify after the final run; owned outputs are removed. CLI/syntax and
root standards/method/simplicity checks pass. Current Python3.14.7 is qualified
here; minimum Python3.10 remains untested.

Final root workflow41 references/37 tools/183 groups, userland quality,17 scoped
links/anchors and whitespace checks pass. Status: complete for this bounded
service/client binding, separate peer review and local integration recorded below.
Documentation impact: this record, root selection, experiment README, Experience,
coverage/workflow and compact evidence. No old native input or seal is refreshed.
[Client mutation completion](FS-CLIENT-MUTATIONS.md) now owns the completed,
reviewed write/namespace receipt layer and its continuation toward process/FILE
write binding. Home creation/layout, native
fit/readiness and fresh authorized execution remain separate. The existing AF08
guest disposition is consumed; full UL/R1/persistent Zsh/packages/ISO remain open.

## Separate review

Peer agent `home_review`, separate from the implementing agent, reviewed the final
runtime/library/checker/test and evidence bytes against the recorded base. Its
[receipt](../evidence/filesystem-home-wire-2026-10-24/peer-review-checks.json) binds
source/document identities,135 child results, six named semantic markers, final
CLI identity and fresh documentation gates. It independently verified final
frozen inputs and absence of the owned work root; it did not rerun runtime tests.
No unresolved findings. The checker optimization and capacity-wording findings
are resolved. This is ordinary peer-agent source/evidence review, not human,
specialist, independent native execution or release acceptance.

Final checker SHA256
`5f24e1da0088ed3d7bb7b802873e3ec12844150d58e76332f69e6b7c007cfe18`
matches both final behavior and CLI evidence. The integrating agent also rechecked
all frozen behavior inputs, unchanged target base and configured `.githooks`.
No broad or unchanged runtime suite is repeated for this review reconciliation.

## Observed integration

Normal commit with configured `.githooks` produced
`71d17efe3571c698b806748052de12a66bd812bc`, tree
`3df04ef4ef21bbc1103c399c839273708ceec351`, matching the reviewed staged candidate.
The reviewer separately confirmed the final review-record additions before commit:
FS-HOME-WIRE SHA256 `80cfc46f814162f05a92044ae6ab57012b6f9a32fb045424d2aea31b222b6561`
and evidence README `e15a00e672c881a0028c8eb73a9a30c4556aa5b3b56b61c798376401e7641a88`.
The integrating agent confirmed clean work and unchanged base, fast-forwarded
`codex/fs-home-wire` into `codex/consolidate-system`, then verified the exact same
commit and tree. Main remains `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`.
No push, guest or native-input refresh occurred. This observation and parent/index
routing are documentation-only reconciliation; final runtime/checker inputs stay
exactly those qualified and reviewed above.
