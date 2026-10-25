# Command I/O integration candidate

This separately selected `--command-runner` experiment runs a C runner and a real
C byte-counting command through strict musl on ABI 9. It is an Aether-local
integration candidate for userland review, not an agreed shared standard or
independent userland adoption. Old producer modes and consumer pins are preserved.
Aether-standards retains canonical cross-project normative ownership.

The Rust broker alone owns two backend records, positions and alias lifetimes.
Input is immutable `abcdef` (or empty in the empty-input case); output is a distinct
64-byte scratch file. Parent bindings are 3/read and 4/read-write. Child bindings
are 0/read and 1/write. Caller identity comes from the private channel pair.

File requests retain 32-byte framing: operation/read=1/write=2/close=3, reference,
FD, count, then 16 payload bytes, all integers little-endian u32. Counts 0–16,
short reads/EOF, rights checks, padding, consuming close and backend errors follow
[NATIVE-FILE-IO](NATIVE-FILE-IO.md). Replies have signed result at 0 and data at 16; other bytes are zero.
References are caller-, record- and generation-bound; they never expose a backend
handle. No open, seek, dup, arbitrary FD or ambient standard stream is supported.

Launch uses a fixed 384-byte frame. Its 32-byte header contains operation 4,
version 1, argc, envc, entry count 2, then zeros. Bytes 32–63 contain the NUL-padded
command name `bytecount`. Two 32-byte entries at 64 and 96 contain source reference,
source FD, destination FD, rights, then zeros. Input must be first, destination 0,
rights 1; output second, destination 1, rights 2. Bytes 128–383 contain eight
32-byte NUL-padded strings: argc arguments followed by envc environment strings,
then zero unused slots. Bounds are argc 1–4 and envc 0–1; unused slots must be zero. The only
permitted environment string is `LC_ALL=C`, at most once. Startup bytes are copied
before native admission. Packed environment strings are translated to the native
startup record's fixed slots 4–7. Channel transfers are capped at 16 bytes; the
384-byte user-space frame is never submitted as one native transfer. Names/strings
never grant executable or file authority.

The broker incrementally receives this fixed frame without blocking the other
client. Even invalid launch headers require all 384 bytes; EOF mid-frame aborts
the bounded experiment. Unknown name returns ENOENT; malformed startup/entries
EINVAL; wrong rights EACCES; invalid source EBADF; existing child EBUSY. Validate
all fields before allocation. Reserve both child channels, invoke existing paired
native launch, and publish both aliases only after success. Failed reservation or
launch closes temporary endpoints; finite channel generations are not refunded.
No file position/content changes occur on admission rejection.

Successful launch replies contain result 0 and a generation-scoped receipt at 4.
Collection is a 32-byte request with operation 5, receipt at 4 and remaining zeros.
It belongs to the parent connection independently of file lifetime. Pending is
EAGAIN, absent/stale/consumed is ECHILD, child caller is EACCES. Success replies
contain actual terminal detail at 8 and kind at 12 with the receipt at 4. Collection
consumes once; native reclaim remains separate. Normal exit, fault and stop are
never conflated. Failed reply delivery is unknown and aborts this experiment;
there is no automatic replay or recovery service.

One 32-byte bootstrap contains result 0, first reference/FD/rights at 4/8/12,
second reference/FD/rights at 16/20/24, reserved zero at 28. The local libc candidate
validates both before publishing bindings. It stores no offset. Public read/write
make at most one 16-byte broker request (larger libc calls return short counts).
A malformed/lost reply poisons the connection. Close consumes the local binding
before delivery. Null nonempty buffers and counts above SSIZE_MAX reject locally;
zero-length calls still validate binding/rights. Arbitrary bad non-null pointers
are not safely probed by this fixture and may fault the caller.

The command's source uses public read/write/close only; transport and bootstrap
live in a separate adapter object. `bytecount --decimal`, `LC_ALL=C` reads until
EOF, handles short writes, emits decimal count plus newline, closes and exits 0.
The bounded runner probe submits startup bytes, mutates its source after
admission, closes its input alias while the child retains one, and collects actual
status. Its output alias observes the shared position at EOF; byte verification
uses the broker's separate backend authority, not an invented seek operation. The broker independently
checks exact backend bytes, input preservation and final close before six native
reclaims across two rounds. Full CR-01 also needs independent userland adoption,
expanded failure/recovery acceptance and packaged reconstruction; this candidate
alone cannot close that milestone.


## Reproduction and acceptance

```sh
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Nine final native cases pass:

| Case | Required observation |
| --- | --- |
| positive | Command computes `6\n`, exits 0; exact backend output and six reclaims |
| empty-input | Identical command ELF computes `0\n`, exits 0; same cleanup |
| rejected-launch | Actual native startup rejection returns EINVAL; explicit first-round retry succeeds without spending child generation |
| partial-reservation | Hold one channel so second reservation fails; EBUSY, all temporary endpoints closed, explicit retry succeeds |
| short-write | Backend forwards at most one output byte per operation; real libc caller loops and exact output remains `6\n` |
| full-output | Preseed output with 64 `!` bytes and position at capacity; backend returns ENOSPC and the command reports write failure with exit 82, runner collects that actual result, bytes remain unchanged and cleanup completes |
| wrong-startup | Alter copied option; command exits 80, runner rejects at 69, broker 970/reclaimed 0 |
| wrong-status | Actual command exit 0 changed in reply; runner rejects at 69, broker 970/reclaimed 0 |
| skip-write | Acknowledge without writing; actual command exit 0, independent storage verification rejects at broker 985/reclaimed 0 |

The six successful test scenarios require exact terminal order 2/0/1 in both
rounds, command exit 0 (82 only for expected output failure), runner-probe exit 29,
backend exit 17 and six reclaims. Probe exit 29 is the harness convention, not the
proposed public `aether-run` exit mapping. Negative scenarios require ordered
command/runner/broker context and the designated panic, never just any failure.
The adapter bootstrap independently probes denied opposite-direction I/O, missing
FD 2, and errno-preserving zero-length input through public libc calls.

The runner probes unknown name, duplicate destination, widened output rights,
wrong source and bad argc before the successful request. The command asserts argc,
argv and `LC_ALL=C`. Rejection injection occurs once in the first round: temporary
channel allocation spends finite generations even after rollback. A rejected
launch does not spend the child's native generation. This is a demonstrated
bounded retry schedule, not an unlimited-retry guarantee.

Link-map checks require actual musl read/write/close archive members. All built
ELFs are inspected for undefined symbols and Linux `syscall` instructions; neither
is permitted. The accepted broker is 6936 bytes within 8192. Base runner, backend
and command ELF sizes are 11440, 994728 and 12312 bytes, with 5, 50 and 5 LOAD pages
respectively. LOAD pages exclude startup stack/TLS and runtime allocations; this
is not a peak-memory measurement. Native loader limits remain enforced.

[Retained evidence](evidence/native-command-io-2026-09-05/README.md) pins final
sources, tools, artifacts, serial logs and affected regressions. Initial compile,
loader, transfer-length, environment-slot and retry-budget failures were corrected;
only the final complete run is acceptance evidence.

## Remaining boundary

This repository supplies a small integration candidate and conformance runner
probe, not a general `aether-run` CLI. The command source is separate from its
adapter and computes output from real reads; it does not hard-code the answer.
Userland still owns the production FD facade, runner/frontend and independent
acceptance. The latest inspected userland milestone was UL-053 (public two-byte
read/close); UL-054's general-I/O handoff remains independent. No sibling source,
consumer pin or canonical owner-review record was changed.

The reply-failure extension below covers selected local reply faults. This suite
does not prove remote recovery after unknown outcomes, cover faults at arbitrary
I/O phases or stop, inspect
arbitrary invalid user pointers safely, or reconstruct packaged artifacts. The
code aborts on uncertain transport rather than recovering/replaying. Those remain
explicit CR-01 acceptance work alongside independent consumer integration; no
shell, fork/exec, service-policy composition or release milestone is closed here.


## Terminal-kind extension

The terminal-kind acceptance extension uses two command variants after writing their
normal output but before closing either inherited descriptor: normal return 134
and an intentional invalid instruction (native fault detail 134, kind 2). Keeping
the numeric detail identical forces collection to distinguish terminal kind.
Both variants must preserve exact output, remove both abandoned child aliases,
allow the parent to consume the actual result once, and complete two rounds with
six reclaims. A broker mutation reporting the fault as normal kind 1 must fail at
the parent's result assertion. This tests observed fault cleanup, not signal
translation, supervisor recovery or an unknown-delivery resolution protocol.


The extended suite has twelve cases: the original nine plus `normal-nonzero`,
`child-fault` and `fault-as-exit`. The first two finish both rounds with exact
terminal ordering and six reclaims. The last requires the actual child record
(kind 2/detail 134), parent rejection (kind 1/detail 69), broker 970/reclaimed 0
and the designated profile panic. The variable instruction address in the fault
log is diagnostic; the oracle matches complete stable terminal records.

[Terminal extension evidence](evidence/native-command-terminal-2026-09-05/README.md)
is separate from the immutable original nine-case bundle. Consumers can continue
adopting that original bundle; this extension changes no request format, base
command behavior, kernel source, quota or consumer pin. Public exit mapping and
POSIX signal/wait-status translation remain userland policy. A fault detail of
134 is not itself an encoded POSIX wait status or evidence of a normal exit.

## Reply-failure test plan

The next AT-COMMAND-RUNNER extension injects a discarded successful read reply,
malformed read metadata, and a discarded successful close reply inside an isolated
client adapter build. The broker has already completed the real operation. Read
failure must report EIO without publishing bytes; close is locally consuming even
when completion becomes unknown to the client. Once poisoned, read/write/close
and launch/collection helpers must produce no further channel syscalls. Tests count
actual channel calls, preserve buffer sentinels, check EIO/EBADF and require exactly
one injection. They do not pretend to lose packets in the kernel or reconcile the
remote outcome. These are deliberate rejected workloads with exact witness exits;
no recovered remote cleanup or full CR-01 pass follows from them.

Affected scope: user-space command adapter/test harness only; unchanged ABI 9,
rights, quotas and consumer pins. No new dependency or unsafe pointer facility is
introduced. Run the full command suite, inherited-launch and connections regressions,
plus host/workflow checks. Retain every attempt on frozen sources. Existing C files
keep their current formatter style for this behavioral change; new test source uses
the approved four-space C configuration. Public-pointer assumptions remain as above.


The extended suite contains sixteen cases. `drop-read`, `corrupt-read` and
`drop-close` require child witness exit 84: all local errno, buffer, one-injection,
consuming-close and no-further-channel-call checks passed. The normal runner then
rejects the witness exit at 69 and the broker aborts at 970/reclaimed 0. A disabled
channel poison guard (`allow-poison-traffic`) must instead be caught at child 93
when a forbidden launch exchange succeeds. It uses the same exact parent/broker
rejection context. A timeout, unrelated panic or different witness exit cannot pass.

These are test-only client substitutions, not production fault switches or an
independent userland acceptance. The original command still performs actual libc
I/O; its twelve existing cases must remain passing. The adapter's raw channel
counter includes partial operations and EAGAIN attempts, so unchanged counts after
poisoning establish no transport activity rather than just no successful replay.
The injection discards/corrupts an already received response; it does not emulate
a kernel packet-loss path or prove recovery from a partial response still queued.

[Reply-failure evidence](evidence/native-command-replies-2026-09-05/README.md)
retains every attempt and distinguishes local fail-closed behavior from remote
cleanup. No reclamation is claimed for the intentionally aborted uncertain cases.
The approved coding configuration applies to the new probe; existing adapter files
retain their prior LLVM formatting for this behavioral change, as planned above.

## Atomic bootstrap test plan

AT-COMMAND-RUNNER will corrupt only the second binding of a fully received child
bootstrap, separately testing its reference, descriptor number and rights. The
first binding remains valid. Rejection must publish neither binding: public read,
write and close on descriptors 0 and 1 must return EBADF, preserve a destination
sentinel and make no channel calls. A test-only early-publication mutation must
be caught by the same witness. No command body runs after a rejected bootstrap.

This tests the existing one-shot startup adapter, not re-bootstrap, partial-frame
recovery or a malicious kernel. Injection is local after receipt; broker-owned
aliases remain subject to the existing fatal workload rejection, with no cleanup
claim. Authority, ABI, quotas, buffer lifetimes and dependencies stay unchanged.
The new probe uses approved C formatting; existing transport/adapter files retain
LLVM two-space formatting for this scoped test change. Run the complete command
suite, inherited-launch and connections regressions and host/workflow checks on
frozen sources; retain all attempts and exact witness outcomes.

The completed extension brings the command suite to twenty cases.
`bootstrap-reference`, `bootstrap-descriptor` and `bootstrap-rights` require child
exit 95 after all EBADF, buffer and no-traffic checks.
`bootstrap-early-publication` requires child exit 97 at the live-binding guard.
All four require the subsequent exact parent exit 69 and broker result
970/reclaimed 0; generic failure cannot satisfy the oracle. The three corruptions
are applied to received byte offsets 16, 20 and 24 respectively.
[Retained evidence](evidence/native-command-bootstrap-2026-09-06/README.md) includes
all twenty command cases, fifteen regressions and host/process checks. This is
producer conformance evidence, not independent consumer adoption.

## Malformed launch test plan

Extend AT-COMMAND-RUNNER with a parent that sends a bounded table of complete
384-byte malformed launch frames before a valid launch, in both generations.
Cover version/count bounds, header and entry reserved bytes, command-name padding,
nonterminated strings, argument/environment padding, forbidden environment and
unused slots. Each rejection must have its exact errno and zero reply bytes 4–31
(no receipt); retry must preserve stream framing, launch capacity, input/output
positions and the normal two-round/six-reclaim result. A broker mutation that
accepts version 2 must be detected by the parent's same rejection check.

This changes only the existing user-space fixture and harness; it introduces no
ABI, dependency, authority or quota change. Buffers remain synchronous stack
buffers; ownership and reservation stay with the existing broker. Validation
remains before reservation in the normal build. Complete-frame rejection does
not establish truncated-frame or unknown-delivery recovery. Run the full command,
inherited-launch and connection suites plus host/workflow checks on frozen bytes.
Use approved formatting for the new C table/probe, retain LLVM formatting in the
existing C helper and Rust 1.98.0 edition 2024 formatting in the broker; do not
migrate unrelated source. Retain all attempts and update this reference and STATE.

The completed suite has twenty-two cases. `malformed-launch` sends the 22-entry
corpus in `user/native-command/launch-probe.h` once per generation (44 rejected
requests), followed by the unchanged valid command path. It requires the normal
ordered terminal records and broker 100/reclaimed 6. `allow-launch-version`
bypasses only version validation in an isolated broker build and requires parent
103 followed by broker 970/reclaimed 0. No arbitrary panic or timeout passes.
The normal broker still validates before `admit`; successful retry and backend
checks witness available capacity and unchanged shared offsets/data, not unlimited
rejection endurance or a new channel-generation refund guarantee.
[Evidence](evidence/native-command-launch-2026-09-06/README.md) retains all command
cases and selected regressions on matching source hashes.

## Truncated launch test plan

Send 0, 1, 4, 16, 31, 32 and 383 bytes of an otherwise valid launch, then close
only the parent's sending channel while the parent remains live. Drain queued
prefix bytes before recognizing EOF. Before child admission, EOF must terminate
the bounded broker with result 1100 plus the exact accumulated length, after
checking unchanged parent/child aliases and file positions. No child admission,
reply or worker terminal record is allowed. Other connection EOF remains fatal.
A test-only zero-padding broker mutation at length 383 must instead be caught by
the parent's forbidden-reply witness (exit 104, then broker 970).

Scope: existing Rust broker diagnostics and C conformance clients, no kernel ABI,
new dependency, authority or quota change. This is explicit fatal containment,
not remote cleanup/reconnection or supervisor-death recovery. Stack buffers remain
live for synchronous native calls. Parent polling and QEMU have existing bounded
limits; a timeout or unrelated failure cannot pass. Freeze source for command,
inherited-launch, connection and host/workflow suites and retain every attempt.
New C uses approved formatting; legacy helper uses LLVM style and Rust uses
1.98.0 edition 2024, with unrelated format migration excluded.

The completed extension brings the suite to thirty cases. `launch-eof-N` covers
N = 0, 1, 4, 16, 31, 32, 383 and requires broker result 1100 + N/reclaimed 0,
with no worker terminal records. Pre-admission EOF now reports this diagnostic
after asserting live aliases and positions are unchanged; other EOF remains 990.
The `pad-launch-eof` mutation invents the last zero byte of a 383-byte frame; the
parent drains the forbidden 32-byte reply and exits 104, requiring broker 970.
Draining avoids racing reply completion with parent endpoint teardown. The normal
parser never pads missing bytes. This does not cover peer exit racing buffered
requests: the existing terminal-first path remains separate.

[Final evidence](evidence/native-command-eof-2026-09-06/README.md) includes all
30 command cases and 15 regressions. The separately retained initial source passed
native tests but had a comment-format failure; the final run also strengthens the
forbidden-reply control. Both attempts have their own source archives.

## Runner startup carrier v1

Producer review of [UL-059](reviews/ul-059-2026-09-06/README.md): proceed with an
opt-in local startup carrier, preserving ABI 9 and exit-29 fixtures. Native Args
has four argument slots; runner invocation needs up to six. The proposed carrier
delivers public runner arguments as data on its existing scoped bootstrap channel,
not in the kernel's native argv vector. The native entry remains the private
`client` trampoline. Userland must review/adapt this distinction before adoption.
No ambient grants or argument-derived authority are added.

The record is exactly 224 bytes: magic `AERUN001` at 0–7, little-endian argc at
8–11, zeros at 12–31, then six 32-byte slots. argc is 1–6, each active slot has a
NUL and zero padding; unused slots are zero. argv[0] must be `aether-run`. Empty
subsequent strings are allowed. This validates transport, not CLI grammar: missing
command, options and slash policy remain userland usage decisions. No environment
is carried; UL-059's LC_ALL=C child policy remains separate.

The producer validates the immutable embedded record before creating workers, then
sends it before the existing two-binding bootstrap in opt-in builds. The parent
validates the complete record before copying/publishing its private argument
storage; it must not call the public CLI on partial/rejected startup. Kernel argv,
wire launch frames, quota and legacy mode do not change. Build-only embedding uses
AETHER_RUNNER_STARTUP with an exact artifact/hash receipt; it is not target ambient
environment or a new public CLI flag.

Pre-implementation tests: native three/six-string witnesses, caller-buffer mutation
after copy, 31-byte and empty argument retention, invalid version/count/padding
and unterminated-slot rejection before any terminal record. A changed valid string
must fail the independent parent witness. Host encoder tests cover byte/count
bounds and rejection without truncation. Run full command, inherited-launch,
connection and host/workflow suites on frozen bytes, retain all attempts. New C
uses approved formatting, legacy helper LLVM style, Rust 1.98.0 edition 2024. No
new dependency or unsafe pointer facility; buffers are synchronous and private.

This does not implement the public CLI or claim AR-01–14 acceptance. Public mapped
results must remain separate from exact native kind/detail and cleanup/unknown
state. Help needs a separately reviewed output grant; no stderr is invented.
Userland UL-063/058 reviews and package/service owner acceptance remain pending.

Carrier qualification: the suite now has 39 cases. `runner-startup` and
`runner-startup-wide` independently check the three/six supplied strings after
copy and source-buffer mutation, then run the original command/exit-29 path with
six reclaims. Invalid magic version, zero/seven count, reserved bytes, unterminated
slot and nonzero unused slot require broker 994/reclaimed 0 before any worker
terminal record. `startup-changed` is syntactically valid but changes a requested
argument: the parent drains the following binding frame without publishing it,
exits 110, and broker must reject at 970. The probe does not forward these arguments
to the command yet; public parsing and AR-04 consumer observation remain open.

`scripts/runner_startup.py` encodes this record for the existing command suite.
Its six host tests run via `zig build test` (or
`python3 -m unittest discover -s tests -p test_runner_startup.py`). The harness
records embedding environment and exact startup artifact digest/size per case.
Opt-in broker size is 7448 bytes within 8192.
[Retained evidence](evidence/native-runner-startup-2026-09-06/README.md) contains
the initial control-ordering failure and final 39 command/15 regression passes.
This is Aether's scoped producer implementation/review, not acceptance on behalf
of userland, sys-init, pkg-mgr or the standards owner.

## Collected runner result mapping

Next opt-in producer experiment maps an observed, consumed child result after
required local closes: normal kind 1/detail 0–255 retains its value; other kinds
or out-of-range detail map to 1. Cleanup failure also precludes success. Preserve
raw child terminal records and separate parent terminal/public exit, independent
backend verification and six native reclaims. The legacy exit-29 mode is unchanged.

Native launch currently masks normal detail to eight bits, so out-of-range and
cleanup-false mapping inputs are direct policy checks, not claims of kernel
out-of-range or failed-remote-cleanup witnesses. Native tests cover normal
0/1/2/64/125/126/127/134/255 and actual #UD detail 134/kind 2. Ignoring kind and
forcing nonzero status to zero must be rejected by the owner. This phase only
qualifies completed child-result mapping; pre-admission/unknown delivery, help,
public parser integration and structured recovery evidence remain open.

The broker accepts mapped results only after child termination and consumed
collection, then independently verifies all aliases, positions and reclamation.
Conformance assertions in this opt-in parent fail with 1; unexpected results
remain rejected by the bounded broker, not generalized failure recovery. No new
wire operation, authority, ABI, quota, dependency or unsafe facility is added.
Apply approved formatting to new C policy; preserve LLVM style in legacy C and
Rust 1.98.0 edition 2024 style. Run full command/inherited/connection suites and
host/workflow checks on frozen sources, retaining all attempts.

Qualification now contains 51 command cases. `public-exit-N` covers
N = 0, 1, 2, 64, 125, 126, 127, 134, 255; `public-fault` observes actual kind 2
and detail 134, mapping only the parent exit to 1. Every accepted case requires
both exact terminal sequences and broker 100/reclaimed 6 across two generations.
`public-ignore-kind` requires actual child kind 2/detail 134, incorrect parent
134, then broker 970; `public-force-zero` requires child 64, incorrect parent 0,
then broker 970. All earlier 39 cases remain intact. The mapped broker is
7064 bytes, within 8192.

`result_policy_probe` directly checks 256/UINT_MAX, non-normal kinds and
cleanup-false inputs, including child zero plus cleanup false -> 1. These direct
policy inputs are not failed-cleanup or out-of-range native terminal evidence.
The current native launch kernel masks normal exit status to eight bits.
No fabricated wide terminal record is introduced.

[Retained results](evidence/native-runner-results-2026-09-06/README.md) bind the
51 command cases, 15 regressions and host checks. Startup carrier and mapped-result
variants are separately qualified here; combining them with the userland parser
and full error/cleanup/recovery evidence is the next integration step.

## Combined startup and result forwarding

The next producer witness combines runner_startup and mapped_results and forwards
validated private carrier strings into the existing copied child launch frame.
The fixture explicitly selects starting slot 1 (three-string carrier) or 2
(six-string carrier containing --); it does not parse public CLI options or infer
authority from arguments. Userland's checkout still has only its fixed client
runner, so public parser integration is pending instead of duplicated here.

Require exact child argv[0], two/four strings, empty/31-byte payload and sole
LC_ALL=C environment; caller frame mutation after spawn must not alter native
startup. Combine normal results 0/64 and actual #UD mapping to 1 with independent
file verification and six reclaims. A changed forwarded byte must be caught by
the child before I/O, then parent and broker reject at exact known statuses.
Keep the earlier standalone carrier/result cases intact. No new ABI, quota,
dependency, rights or unsafe boundary: fixed private arrays feed synchronous
serialization, and the owner still validates/copies before admission. New/edited
probe uses approved C format; legacy helper/program retain LLVM style. Run command,
inherited/connection and host/workflow checks on frozen sources and retain attempts.

The combined extension passes four new cases (55 total). `combined-startup`
forwards two child strings and maps exit 0; `combined-wide` forwards four,
including empty and 31-byte strings, and maps exit 64; `combined-fault` uses the
same wide startup with actual #UD kind 2/detail 134 mapped to parent 1. All three
require exact two-generation terminal sequences and broker 100/reclaimed 6.
`combined-corrupt` changes byte 224 of the launch frame (fourth argument); the
child rejects at 80, parent at 1 and broker at 970/reclaimed 0. The combined
broker is 7544/8192 bytes. The independent child observer verifies no additional
environment entries and a terminating argv pointer, before any file I/O.

[Evidence](evidence/native-runner-combined-2026-09-06/README.md) retains all
55 command cases, 15 regressions and host checks on matching final sources.
This closes the producer's combined forwarding witness, not userland-owned
CLI parsing, independent consumer adoption, help grants or unknown-outcome
recovery. The explicit FORWARD_FIRST fixture input must be replaced by the
userland parser's validated selection during actual consumer integration.

## Runner-only empty-output prerequisite

The command suite also selects `-Dnative-runner-local=true` for the bounded
`runner_local_empty` owner witness. This requires a native image and `-Dsmp=false`;
it selects an exact four-reclaim connections test oracle. It adds no syscall,
stream role or native capacity and does not change default six-reclaim behavior.
The parent closes existing bindings 3 and 4 without issuing any other request.
The owner verifies untouched `abcdef`, empty output, generation-bound references,
consumed backend handles, normal parent status zero and explicit closes before
terminal completion. Parent and backend are reclaimed in that order twice. The
unused third envelope image is never admitted. Channel quiescence and zeroed
backing remain kernel completion requirements.

`local-empty` passes only with ordered slots 0/1 in generations 1/2 and result
100/reclaimed 4. `local-skip-close`, `local-launch`, `local-stale`, `local-status`
reject at owner results 1201, 1202, 1203, 1200 respectively with zero reclaims.
`local-premature` rejects result 100/reclaimed 2; `local-legacy-gate` rejects result
100/reclaimed 4 under the unchanged default oracle. All reuse the existing smoke
marker and full command-suite invocation above.

This is an empty-output lifecycle prerequisite, not help/version acceptance.
Separate runner stdout/stderr capacities and publication, short/failing delivery,
RL01–12 completeness, owner review and immutable consumer handoff remain open.
See the [implementation contract](evidence/runner-local-empty-2026-09-07/contract.md).

## Experimental runner output roles (AEOUT001)

Selected only by the command suite's `runner_streams` owner/client/backend builds,
using the existing four-reclaim native test oracle. This is a runner-only profile;
child bindings, AERUN001 and old profiles are unchanged. Composing these roles
with child launch and denied-admission outcomes remains subsequent work.

The 96-byte startup carrier has a 32-byte header: magic `AEOUT001`, count 2 and
native generation (little-endian u32), followed by 16 zero bytes. Two 32-byte
records each contain role, reference, FD, rights, capacity (five u32), then 12
zero bytes. Records are ordered stdout (role 1, FD 1, capacity 512), stderr (role
2, FD 2, capacity 256). Rights 2 permits write plus consuming close. References
are `0x75000000 + (role << 16) + generation`. Both complete records must validate
before either binding becomes live. No ambient FD confers a role or authority.

Existing 32-byte file request/reply framing is retained for write/close only.
Reads fail EACCES locally; owner-side operation checks also reject reads, launch
and collect. The owner exclusively owns positions and aliases. The separate
backend owns 512/256-byte append-only scratch sinks and immutable `abcdef` input.
It explicitly grants three private-channel handles in its 32-byte hello at words
1/2/3: 0xf101/0xf201/0xf202. These backend handles are connection-scoped and never
published to the parent. Read=2/write=4/close=3 use the existing backend framing;
closed handles return EBADF. End-of-channel succeeds only with all three closed.
This fixed fixture is not a general filesystem namespace or open API.

The owner checks exact selected text, length and EOF in both sinks by backend
readback, unchanged input, explicit alias closes, exact normal parent status,
all backend closes/stale denial and two-generation parent/backend reclamation.
Malformed second-record rights/role/generation must publish neither binding;
bootstrap failure exits 110 with zero traffic and owner cleanup. Terminal
observation also requires no partial frame and channel EOF before accepting
completion, so queued post-close requests cannot disappear during reclamation. Help/version
text exits zero, usage text exits 64. Text in `user/native-command/text/` is copied
from hashed userland proposal fixtures; this C client does not implement parsing
or claim a released runner version. Output stays in fixture sinks, not a console.

The full command-suite invocation includes atomic-publication and post-close
traffic mutants (1302), plus the same post-close control for local-empty (1202),
normal help/version/usage, one-byte
short writes, skipped/wrong-byte/wrong-sink output, omitted close and malformed
carrier cases. Exact output mismatches reject at owner 1305; missing close at
1303; forbidden traffic at 1302. Four native reclaims are required for successful
completion. Evidence and additional controls are recorded in STATE.

Remaining UL-059 work includes failure cases beyond the scoped witnesses below,
complete denied admission/error witnesses, remaining startup rejection coverage,
reviewed immutable bundle and independent consumer adoption. This is not RL01–12
completion, UL-067 cat authority, renderer conformance or release readiness.

### Deterministic operational failure witnesses

The stream client stops writing after zero/negative progress, attempts each
remaining close once and exits 1 after a delivery or close error. The owner binds
acceptance to the selected failure, exact retained prefix, normal terminal status
1, both consumed aliases and independent backend cleanup. It rejects additional
writes after the selected delivery failure at 1310, missing failure observation
at 1311, and falsely successful terminal status at 1301.

`streams-zero` and `streams-fatal` return zero/EIO after 16 help bytes;
`streams-usage-zero` preserves exactly 16 stderr diagnostic bytes. The 528-byte X
probe in `streams-exhaust` exercises actual backend ENOSPC after 512 stdout bytes;
it is not CLI text. `streams-close-error` preserves complete help output and
returns EIO after consuming stdout's alias, then requires stderr close too.
A complete valid EIO close reply in AEOUT001 explicitly confirms alias consumption
and permits cleanup of the other role. Legacy close handling is unchanged; malformed
or other unknown nonzero close replies still poison the connection. Client close
never claims the separately held backend handle has already been closed.

Controls retry failed output, hide failure as status zero, ignore close failure,
or fabricate exit1 without sending output. The owner must reject each at the
named traffic/status/failure-observation gate before any native reclaim. Successful
failure witnesses still require two generations/four reclaims, untouched input,
exact sink readback and backend close/stale denial. No replay or successful
truncation is accepted. Broader ambiguous transfer/cleanup and denied launch
remain open; bounded reply cuts are specified below.

### Lost and partial replies after a committed effect

The `streams-amb-*` cases close the actual reply endpoint after zero or eight
reply bytes. Write cases commit exactly 16 help/stdout or usage/stderr bytes first;
close cases consume stdout's alias after full help output. The client receives an
incomplete frame, reports EIO, poisons the connection and exits1 after locally
consuming remaining descriptors. A test-only trap counter verifies no further
channel calls, and the owner separately rejects post-cut requests at 1320. Clearing
poison/resuming and hiding failure are deliberate rejected implementations.

At exact normal terminal status1, the owner requires request EOF/no partial frame
and the exact live-alias set: both after lost write reply, stderr only after lost
stdout-close reply. It then retires remaining aliases; a skipped retirement fails
1321 before backend cleanup. The owner independently reads both sinks/input,
closes and verifies stale backend handles and reclaims parent/backend twice.
The already-closed reply endpoint is not closed again. No additional native quota,
wire field or reconciliation API is introduced.

This proves bounded owner-side cleanup after confirmed client termination. The
client has no acknowledgment of committed bytes or remote alias retirement and
must not claim recovery from its EIO result. Pre-effect disconnects, other cut
positions, owner/backend death and general reconciliation remain unqualified.

### Startup field-category rejection coverage

The full command suite adds `streams-start-*` cases for magic/version, role count
one/three, stale header generation, nonzero header padding, duplicate descriptor,
wrong capacity and nonzero record padding. Existing rights, role and reference
cases remain. Each complete malformed carrier requires normal bootstrap status110,
zero request traffic, empty outputs and verified owner cleanup across two generations.
A parser deliberately ignoring capacity must fail at owner1302 on its first request.
This is coverage of every defined carrier field category, not exhaustive byte-level
or truncation/fuzz coverage. No normal wire or capacity behavior changes.

## Combined roles and denied launches (AERIO001)

This separately selected producer fixture has a 160-byte carrier: the AEOUT001
header/record layout with magic `AERIO001`, count4 and four ordered role/FD records.
Roles1/2 retain stdout/write/512 and stderr/write/256. Role3 is child input/read/6;
role4 is child output/read-write/64. All grant consuming close. Runner references
remain `0x75000000 + (role << 16) + generation`; child-source references remain
`0x71000000 + ((role - 3) << 16) + generation`, matching existing fd3/fd4 launch
validation. All four complete records validate before any binding is published.
AEOUT001 and existing startup/child profiles retain their bytes and selection.

The private backend adds handle0xf203 and a separate 64-byte child-output record;
input0xf101 and runner sinks0xf201/0xf202 retain their meanings. This adds user-space
fixture storage/metadata, not kernel capacity. The parent submits the existing
384-byte launch frame. Absent name yields actual validator ENOENT; widened input
rights yield EACCES. EBUSY uses an actual held channel pair so `admit` fails during
partial transport reservation before any native child admission. The held pair is
released. After the second denial, two free pairs must allocate and a third
must return EBUSY, followed
by closure of all probe endpoints. Each pair slot consumes its three-generation
budget on two reservations plus the final probe; the leak control probes early.
This proves bounded reservation restoration, not an
invented errno or an admitted child's exit.

Exactly one request and the selected error must precede diagnostics or closes.
A second launch, collection, child I/O or fabricated status2 is forbidden in this
no-admission witness. Exact copied proposed stderr text, empty stdout/child output,
unchanged input, four explicit alias closes, normal parent status2, all backend
closes/stale denial and two-generation/four-native-reclaim cleanup are required.
An invalid fourth-role grant instead requires bootstrap110 and zero traffic.

Cases `streams-denial-name/rights/busy` exercise the three errors. Controls omit or
repeat a request (1340), corrupt diagnostic bytes (1305), send the wrong wire errno
(parent125, owner1301), or leak the held reservation (1342). These failures occur
before native reclaim; a generic panic/watchdog is not an acceptable oracle.
Denied-launch diagnostic failure cases compose the actual denial with zero/EIO
writes, consumed-close EIO, and actual zero/eight-byte reply cuts. Delivery failure
maps to status1, retaining the denial witness and exact accepted prefix. Every
close is attempted independently: failure closing child input cannot skip child
output. On ambiguity, all four local aliases are consumed without further channel
calls; owner aliases are retired only after terminal plus request EOF. Controls
hide failure as status2, omit the final close, or resume poisoned traffic and must
fail at the named oracle. See the [qualification](evidence/runner-denial-failures-2026-09-07/README.md).
The separate successful-child and composition experiments below cover selected
child outcomes and logical startup forwarding. Remaining RL coverage, affected-owner review,
immutable handoff and independent consumer adoption remain separate gates.

### AERIO001 successful child experiment

The separately selected `success-child` owner/client uses the same four-role
carrier and existing 384-byte launch/32-byte collection frames. Parent fd3/read
and fd4/write become bytecount fd0/read and fd1/write. The owner delays child
bootstrap until parent fd3 has closed, so the child must retain its delegated
input independently. The child reads `abcdef` and writes `6\n` to the distinct
64-byte child sink; both runner sinks remain empty. The shared output cursor
leaves parent fd4 at EOF after collection. No authority or output role is inferred
from the child program's name or status.

Require normal child0/kind1, one consumed collection followed by ECHILD, all four
parent and two child closes, drained requests at terminal, backend readback,
backend close/stale denial and two generations/six native reclaims. The owner
retains backend records until both clients have terminated and their aliases
have closed. Normal and one-byte short writes are selected witnesses. Controls
omit collection (1401), omit runner stdout close (1403), fabricate write success
or route child writes to runner stdout (1405). Generic panic is not acceptance.

The [evidence record](evidence/runner-success-2026-09-07/README.md) defines scope.
This remains a producer conformance fixture, not the actual parser, general process
service or consumer handoff. Unknown collection, remaining RL coverage and
independent owner adoption are open.


### Four-role terminal and logical-startup composition

Selected `success-*` cases now retain actual normal134 versus fault134/kind2,
returning parent134 versus parent1. Collection carries the observed raw kind/detail;
it never infers a fault from a numeric exit. The child intentionally leaves both
aliases live after output in these variants. The owner checks terminal plus drained
request EOF before retiring those aliases, then still verifies all backend bytes,
parent explicit closes and six native reclaims. The retirement-skip control must
reject at1403. Existing ordinary-success child closes remain explicit.

Forwarding cases prepend the existing 224-byte AERUN001 carrier to AERIO001. The
private client decoder validates and copies it, then forwards fixture-selected
slots1/2 into the existing launch request. The independent child observer checks
complete argv/env, including empty and 31-byte strings. Request overwrite before
child bootstrap verifies copied native startup lifetime. Three-string normal0,
six-string normal64 and six-string fault134 cases retain output and cleanup checks.
This uses a fixture-selected argument offset, not the real userland parser.

Controls force normal134 to zero or ignore fault kind (1401), corrupt the fourth
forwarded argument (child80, owner1407), or skip terminal alias retirement (1403).
See [composition evidence](evidence/runner-composition-2026-09-07/README.md).
Malformed composition, unknown collection, remaining RL audit and independent
consumer review/build still need completion before the producer handoff is accepted.


### RL return-candidate coverage

The [RL audit](evidence/runner-handoff-2026-09-07/RL-AUDIT.md) maps all twelve
requested producer cases and explicit consumer/coverage limits. Additional controls
cover usage64 and ENOENT2 with one-byte short writes, a help client attempting op4
(reject1302 before admission), and a second-generation parent presenting the prior
receipt (reject1404 after three prior reclaims). These add no wire fields or grants.
The [return package](evidence/runner-handoff-2026-09-07/README.md) provides exact
source/profile/evidence identity for independent userland review and rebuild;
existing pins stay unchanged and this is not consumer acceptance.

### Lifecycle observation across channel EOF

The bounded command fixture rechecks its holder-scoped child terminal record when
a channel read returns EOF after a running poll. Confirmed termination returns
to ordinary status validation and alias cleanup; EOF alone never confirms exit.
Still-live EOF preserves existing partial-launch/rejection behavior. The
bootstrap-exit-window control models a stale poll and waits for real termination; bypassing
revalidation must reject990 rather than pass the child97/parent69/owner970 oracle.

## Real helper launch fixture — 2026-09-09

The `success-helper-argv` family is an explicit producer-only namespace selection
within the existing command-runner suite. It maps `/inputs/helper` only to the
pinned consumer helper image and requires argc4/envc2, with LC_ALL=C then
WITNESS=value. All original reference/rights, framing, termination and padding
checks remain. Other variants retain bytecount and the original LC_ALL-only policy.
No path lookup or shared wire/version change is introduced. The requester and
child keep separate native connections and existing shared-description lifetimes.
This executes the real helper body, not dash's fork/exec or the complete DASH-argv
script. See the selection and evidence in NATIVE-SHELL-STARTUP and STATE.
