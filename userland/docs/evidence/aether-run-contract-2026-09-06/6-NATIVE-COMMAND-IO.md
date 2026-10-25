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
