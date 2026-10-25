# SESSION terminal/transfer interleaving

Before-code scope: make the suspected owner polling race executable using the
actual Session::poll body. A private source-derived owner releases a worker only
after its first nonterminal observation, confirms real exit or live frozen state,
then attempts the actual channel transfer. Exercise EOF on read and EPIPE on write.
The old owner must fail; if confirmed, the corrected owner may accept those exact
outcomes only after a second observation confirms the same held task is terminal.
Live peers that close their endpoints must still fail. Preserve all input/failed
evidence; do not label the original uninstrumented failure's exact call site known.

Aether owns the fixture and borrowed dispatcher mechanism; sys-init owns its
entry/policy and consuming qualification. No sibling edits or new ABI/grant/kernel
operation. Existing terminal handling, wait collection, descriptor/pipe settlement
and reclaim prerequisites remain authoritative. Never infer terminal from channel
EOF/EPIPE alone, replay a partial request, weaken positive count bounds or hide
other errors. No automatic restart or general recovery framework.

Native tests compile source-derived private copies with a bounded interleaving
hook; production source contains no hook. The worker owns only its existing
endpoints. Synchronous traps borrow live mapped storage; all code is Rust1.98,
edition2024/no_std/panic-abort. Inspect optimized owner bytes/stack and immutable
indirect targets. Fresh real dash immediate/delayed/wide-output plus all11 older
serial cases and full host/pin/workflow checks follow the final frozen correction.
Document limits/results in STATE, ROADMAP and NATIVE-CONNECTIONS; deliver a producer
source correction for sys-init to consume explicitly. Keep failed live-peer/control
runs distinct from acceptance. Archive/read back only newly owned outputs before
removing them; immutable packets and released standards remain unchanged.

Simplicity: removing the terminal check or accepting arbitrary transfer errors is
simpler but permits unjustified cleanup or hides corruption. A second exact-task
observation for only EOF/EPIPE adds no state, abstraction, grant or resource pool.
Reuse the existing terminal/cleanup path; do not introduce an atomic multi-operation
kernel call or repeat supervision policy in the kernel. No compatibility path is
removed; existing consumers need the same correction qualified in their composition.

## Results and producer handoff

Six final native runs use the actual poll body, with only private pre-transfer
release/observation and result-marker hooks. Real exit is published after its
first live observation; actual EOF/EPIPE is independently recorded before checking
the outcome. Old read/write owners fail with the exact owner marker/panic. Fixed
read/write owners confirm terminal, reclaim1 and halt. Live peers close their
respective endpoint and freeze without exiting: both remain owner failures, with
zero terminal/reclaim/settlement/halt. Eight corrupted traces reject. The hooks
never enter production source; no count or terminal result is fabricated.

The correction adds12 lines to `user/native-capacity/session-owner.rs`: only read0
and write-32 re-observe the same held task and return progress after confirmed
terminal handling. Existing handling clears the peer frame and records its real
terminal status; no ambiguous frame is replayed. Actual reclaim remains under the
existing parent/child wait-collection and descriptor/pipe cleanup prerequisites.
Other errors, EAGAIN and positive-transfer bounds remain unchanged.

The frozen canonical userland009 ELFs are reused from the verified prior intake;
fresh current-source Aether owners/kernels qualify immediate,35-second delayed
and wider output workloads. They pass565/4472/853 ticks, delayed3910 idle and10
reclaims each. Three strict comparisons/12 corruptions reject altered bytes,
terminals, idle/cleanup and panic. All11 old ABI23 cases rebuild current owners
around their exact sealed old clients; full133-Python and configured Zig/Rust/
workflow/released-pin checks pass. No unrelated M4/ABI22 run is selected: kernel,
build and those sources are unchanged; this is a user-space dispatcher correction.

Normal owner15232 bytes is48 bytes larger. Raw extraction matches ELF. Conservative
stack3864/4088 is unchanged; all34 indirect sites bind manually inspected immutable
memcpy/memset/memcmp cells, with no indirect jumps. Read-family private probes
estimate3336 stack; write family2792; all raw sizes fit the24KiB profile. Default
worker function56 plus conservative24-byte entry charge fits its64KiB stack.
These are scoped inspection estimates, not a whole-system stack/security proof.
Original generic stack aids and the corrected exact-site aids are retained.

The first two private builds hit the copied8KiB linker limit; their receipts,
compiler errors and sources remain. The existing24KiB recipe corrects the test
profile. Initial six schedules remain distinct from the final strengthened result-
marker qualification. One copied private write stack aid assumed absent memcmp;
the failing aid/log remain, while the final aid binds actual builtin targets.
`preparation-notes.md` records these corrections; no unexpected target failure is
hidden. Final source maps agree and identify only the production owner change.

`owner-terminal.patch`, `owner-after.rs`, source exports and producer-handoff.json
are the scoped producer delivery for sys-init's borrowed dispatcher. Sys-init
must preserve its genuine entry/policy, inspect the resulting linked image/stack
and qualify normal immediate/delayed original-failure schedules plus its remaining
negative controls. No sibling is modified and no messaging/sign-off is performed.
This confirms and corrects an executable race; the original uninstrumented failed
call site and absence of other defects are not established here. Full composition,
independent SDK/review, maintained init recipe, persistent files/packages and R1
remain open.

Reproduce private witnesses from a fresh directory, preserving the resulting
receipts and source exports rather than running sealed tools in place:

```sh
poll_review=$(mktemp -d zig-out/poll-review-XXXXXX)
cp docs/evidence/session-poll-terminal-2026-10-03/run.py "$poll_review/run.py"
cp docs/evidence/session-poll-terminal-2026-10-03/prepare.py "$poll_review/prepare.py"
cp docs/evidence/session-poll-terminal-2026-10-03/owner-before.rs "$poll_review/owner-before.rs"
python3 "$poll_review/prepare.py"
python3 "$poll_review/run.py" old-read-final
python3 "$poll_review/run.py" old-write-final
python3 "$poll_review/run.py" read-final
python3 "$poll_review/run.py" write-final
python3 "$poll_review/run.py" live-read-final
python3 "$poll_review/run.py" live-write-final
```

Sealing receipt: 413 generated file members read back against size/hash
index before18 newly owned VM/build roots were removed. Failed builds, source
exports, first/final schedules, canonical-client runs and older serial regressions
remain retained. No global cache, sibling, source or historical packet is deleted.
