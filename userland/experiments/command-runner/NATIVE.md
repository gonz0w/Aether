# Independent native bytecount integration (UL-057)

Nine native cases pass with an independently authored finite runner, two-binding
libc adapter and the previously host-tested bytecount source. The command source
hash is unchanged from UL-056's 21 host/control outcomes. Its native ELF is 13,504
bytes; the normal runner is 12,440 bytes. Separate entry code installs the validated
bindings before calling bytecount_main. The adapter supplies initialized TLS and
no local file positions. This is actual Aether command execution through musl,
not host emulation or a hard-coded output/exit helper.

The source-rebuilt Aether broker/backend come from the completed
native-command-io-2026-09-05 archive. No sibling or shared transport source changed.
The new client channel object renames the original hook; native-io.c provides the
single active __aether_io. Both bootstrap entries validate before either goes live.
Parent bindings are 3/read and 4/read-write; child stdin/stdout are 0/read and 1/write.
File calls validate local binding/rights/count, issue at most one 16-byte transfer,
validate reply bounds/metadata/padding, then copy caller data. Close consumes the
local binding once. Transfer/malformed file-reply failure poisons the connection;
that mechanism still needs dedicated two-binding failure controls in UL-058.

The runner builds the candidate's 384-byte launch frame with two inheritance entries
and copied argv/env. It rejects unknown name, duplicate destination, widened rights,
wrong source, excessive argc, nonzero unused startup bytes and unsupported version,
then successfully launches. Every rejected launch sends a complete frame, so the
subsequent valid launch exercises alignment. The runner mutates its source buffer
after successful admission; bytecount validates argc, option and LC_ALL. This does
not independently check every startup string (notably argv[0]) or arbitrary mutation
schedules; expanded startup/partial-frame tests remain open.

The runner closes its input alias while the child retains stdin, collects actual
terminal detail/kind once, rejects a foreign and then consumed receipt, observes
output EOF at the shared position, and closes its output alias. The command closes
both standard bindings. Each successful scenario repeats for two fresh generations,
with terminal order command/runner/backend and six reclaims.

| Case | Required outcome |
| --- | --- |
| Nonempty input | Same command computes `6\n`; command 0, runner 29, backend 17 |
| Empty input | Same command computes `0\n`; same successful cleanup |
| Rejected native launch | Explicit EINVAL on first-round attempt; successful retry, both rounds |
| Partial reservation | Explicit EBUSY and rollback; successful retry, both rounds |
| One-byte writes | Command loops over short results and completes exact output |
| Full output | Command returns its real operational exit 1; runner collects 1; successful fixture cleanup |
| Wrong startup | Modified option produces command 64; runner assertion 53; broker 970/reclaimed 0 |
| Wrong reported status | Command actually exits 0; runner assertion 53; broker 970/reclaimed 0 |
| Skipped storage | Command exits 0 but owner output verification rejects at 985/reclaimed 0 |

Positive cases require the unchanged CONNECTIONS PASS marker and exact terminal
sequence; negative cases require exact command/runner/broker contexts with no
success marker. Timeouts, unrelated panics and build failures cannot pass. The
full-output case uses exit 1 from our command, rather than adapting it to the owner
command's private exit 82. The broker already retains actual status, so its source
needed no change.

Exact output and input preservation are checked by the owner broker's independent
backend readback. The userland runner sees EOF after child output because it shares
that position; it does not independently read `6\n` or `0\n` from the start. The
skip-write control exercises this explicit trusted verifier boundary. This resolves
the bounded witness honestly without pretending EOF is byte comparison or adding
a client-local seek.

```sh
python3 experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-command-io-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The pinned 178-file archive, producer summary/report and tested strict-musl/tool
inventory are checked before private builds. Archive links, traversal, duplicates
and unlisted files reject. Owner tools verify boot dependencies. Five independent
ELFs retain static x86-64/TLS/NX/W+X/dynamic/undefined/Linux-syscall checks and maps;
command maps explicitly require musl read/write/close and exclude threaded
cancellation. Source/SDK stability checks pass. Commands and versions retain
Clang/LLD 21.1.8, Rust 1.98.0, Zig 0.16.0 and QEMU 11.1.1. QEMU uses TCG, one CPU,
256 MiB, no NIC, private firmware variables and the pinned 30-second watchdog.

[Evidence](../../docs/evidence/native-command-userland-2026-09-05/README.md) retains
sources, archive, clients, brokers/backends and serial logs. Large generated images
remain in `build/native-command-userland-7qy90ndd` with receipt identities. All nine
cases passed on the first build/run. All three standards checks pass. Older profile
suites were not rerun because their implementation sources were unchanged; the
producer's broader regressions remain separate.

The finite runner intentionally retains the broker's required exit 29 and fixed
startup. It is not the public aether-run CLI, and this does not close full CR-01,
dash/M3 or POSIX spawn/wait. UL-058 adds two-binding bootstrap/unknown-delivery and
malformed-frame/abnormal-child coverage. UL-059 specifies public runner argv/status
integration: the current broker hard-codes parent startup and demands runner 29,
so public exit mappings need an explicit owner contract change. Package reconstruction,
sys-init policy, general FD operations, fork/exec/pipes/TTY and PD review remain open.

## Independent native bootstrap controls — 2026-09-06

```sh
python3 -B experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 \
  --sdk build/native-c-xhkdw6jv --bootstrap-controls
```

The explicit option selects the [reviewed newer producer](../../docs/RUNNER-INTEGRATION.md)
and adds three malformed second-binding cases plus an early-publication mutation.
The actual native adapter receives its bootstrap over native channels; a test-only
link wrapper corrupts a received field. Real musl calls verify EBADF, sentinel and
zero subsequent adapter traffic. Required exits are child95/parent53/broker970,
with child97 for the mutation and reclaimed0 in all four. These are semantic
rejection witnesses, not remote cleanup. No success marker may appear.

All 13 cases pass. The original nine-case invocation above also passes separately;
default pins and all five legacy client bytes remain unchanged. Four new clients
pass existing ELF/musl inspections, and 21 host/control regressions pass.
[Evidence](../../docs/evidence/native-bootstrap-userland-2026-09-06/README.md)
retains exact snapshots, traps-oracle source, logs and artifacts. NB-02–04 and
public CLI integration remain open; the newer producer's carrier is not yet used.

## Independent native reply controls — 2026-09-06

```sh
python3 -B experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 \
  --sdk build/native-c-xhkdw6jv --bootstrap-controls --reply-controls
```

The reply option adds lost read, malformed read and lost close after a complete
real service reply, plus a disabled-poison mutation. Read sentinels, consuming
close, exact musl errno and zero later adapter channel calls are required.
Expected child84 (mutant94), parent53 and broker970/reclaimed0 distinguish the
local safety witness from native recovery. No normal success marker is allowed.
The mutation's first forbidden channel attempt is caught before issuing its trap.

All 17 combined cases, nine original-pin regressions and 21 host tests pass.
Nine prior client ELFs are unchanged; four new reply clients are inspected.
[Evidence](../../docs/evidence/native-replies-userland-2026-09-06/README.md)
retains exact sources, replies-oracle code, artifacts and serial logs. NB-03/04
and UL-059 remain open; this option does not enable the public startup carrier.

## Independent native launch framing — 2026-09-06

```sh
python3 -B experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 \
  --sdk build/native-c-xhkdw6jv --bootstrap-controls --reply-controls --launch-controls
```

The launch option adds a 22-entry complete-frame rejection corpus repeated in
both generations before a valid command, seven parent-live truncated-frame EOF
cases, and two existing producer mutations. Exact errno/zero receipts and aligned
follow-on are required. Prefixes 0/1/4/16/31/32/383 require broker1100+length with
no terminal records. Accepting a bad version must be caught at parent103;
padding a missing final byte at parent104 after draining its forbidden reply.
Both mutations require broker970, not arbitrary failure. EOF is fatal containment,
not recovery. Test-only raw endpoint operations do not change the normal adapter.

All 27 combined cases, nine original-pin and 21 host/control regressions pass.
Thirteen prior client ELF bytes remain identical. [Evidence](../../docs/evidence/native-launch-userland-2026-09-06/README.md)
retains the eight added clients, sources, corpus, artifacts and raw logs.
NB-04 and public startup/result integration remain open.

## Independent native terminal distinction — 2026-09-06

```sh
python3 -B experiments/command-runner/native.py --aether ../aether \
  --producer ../aether/docs/evidence/native-runner-combined-2026-09-06 \
  --sdk build/native-c-xhkdw6jv --bootstrap-controls --reply-controls \
  --launch-controls --terminal-controls
```

The terminal option adds normal exit134 and actual invalid-instruction fault134
before bytecount closes its aliases. Parent variants require native kind1/2,
retain one-time collection and exact output/cleanup checks, and finish two rounds
with six reclaims. The producer's wrong-kind mutation is caught at parent53 with
the actual child kind2/detail134 and broker970/reclaimed0 retained. The normal
parent still exits29: no public runner or POSIX signal mapping is implied.

All 30 combined native, nine original-pin and 21 host checks pass. Twenty-one
prior ELF bytes remain unchanged; four terminal variants are inspected.
[Evidence](../../docs/evidence/native-terminal-userland-2026-09-06/README.md)
retains exact sources, records and cleanup. NB-01–04's scoped witnesses now exist;
independent reviews, public startup/result integration and recovery remain open.

## UL-059 carrier integration checkpoint

`--startup-controls` selects the reviewed combined producer and three new client
ELFs: parser-selected parent, corrupted-fourth-argument parent, and independent
child startup observer. The simple, delimiter and wide-vector cases each finish
two generations with child0/parent29/backend17 and six reclaims. Corruption requires
child80/parent53/broker970, without a pass marker. No producer source modification
or mapped_results mode is used; native argv=["client"] remains distinct from the
logical AERUN001 input. `--startup-controls` alone runs 13 native cases; with all
four earlier control flags the [recorded run](../../docs/evidence/runner-startup-2026-09-06/summary.json)
passes 34. Existing tool, SDK, process and guest limits apply. The ordinary nine-case
pin remains the default. Native malformed carrier transport and public local
outcomes remain separate from host startup controls and these positive witnesses.

## UL-059 mapped-result checkpoint

The [mapped-result run](../../docs/evidence/runner-mapped-2026-09-06/summary.json)
passes 47 combined native cases and nine original-pin regressions. Ten new
positives retain the child's nine selected normal exits or map actual fault134/
kind2 to parent1. Each completes two generations, independent output verification
and six reclaims. Ignoring fault kind, forcing child64 to parent0, and a local
close-error report require exact child/parent/broker970 rejection records.
The cleanup hook checks full raw child0/kind1/receipt and cleanup=false at policy
entry. This is not failed remote close or accepted recovery. Prior28 client ELF
hashes are identical; 14 mapped clients are added. Native out-of-range normal
detail and stop remain unexercised here; their policy tests are host evidence.
Public help/usage/precondition outcomes and unknown recovery still need owner
acceptance. No mapped mode is selected by default.

## UL-059 mapped uncertainty checkpoint

[Six native controls](../../docs/evidence/runner-native-uncertainty-2026-09-06/summary.json)
cover lost/padded admission and lost/padded/foreign-receipt collected results,
plus a retry mutation. The wrapper validates the real original reply before
injection and checks runner return1, one injection and no subsequent guarded
exchange/channel/read/close/policy calls. Admission witnesses exit101 without
assuming child scheduling; collection requires actual child0 then witness102.
Retry exits109 before another exchange reaches the adapter. All reject at
broker970/reclaimed0. No remote cleanup or recovery acceptance follows.

All 53 combined native and nine default-pin cases pass; 42 prior client ELFs
remain identical. Only opt-in test wrappers/drivers changed. Native malformed
startup carrier and pending-budget coverage remain distinct follow-ons.

## Native startup rejection checkpoint — 2026-09-06

[Nine native controls](../../docs/evidence/runner-native-startup-2026-09-06/summary.json)
reject corrupted real carrier magic/count/reserved/slot padding, invalid second
binding rights, and receive prefixes0/223/255. Witness111 checks unpublished
arguments/references, real musl EBADF on FD0–4 and no auxiliary lookup/channel
activity on retries. A private early-argument-publication adapter mutation triggers
witness112 before the following receive. No child is launched. Exact parent-only
terminal records and owner970/990 with reclaimed0 establish deliberate rejection,
not cleanup or recovery. Original complete records are validated before mutation;
partial receives are local fault injection, not a remotely truncated producer.

All62 combined native cases and nine original-pin cases pass; all48 prior client
ELFs remain identical. Host startup270+2 mutations, mapped25+4, parser1293+2,
result28159+4 and21 command regressions pass. Source review corrected intermediate
pointer arithmetic in the new test witness; the superseded attempt and corrected
rerun are retained. Production code and producer/SDK pins are unchanged.
Native pending-budget controls, independent reviews and owner acceptance of local
help/error/output and unknown-resource recovery remain open. UL-059 stays active.

Select `--carrier-controls` with `--bootstrap-controls --reply-controls
--launch-controls --terminal-controls --startup-controls --mapped-uncertainty`
and the pinned combined producer for all62 cases. Carrier mode implies mapped
producer/build support and alone runs31 cases (nine legacy,13 mapped and nine
carrier cases); it does not alter the default producer. `carrier-native.c` links
real channel/getauxval wrappers and parser/startup adapter, plus actual musl
read/write/close. Other artifacts keep their existing linkage. Production adapter
publication order remains unchanged; only the private early-arguments mutant
publishes before binding validation. The existing native180s/file512MiB and
30-second/no-NIC guest limits apply.

## Native collection-budget checkpoint — 2026-09-06

[Four native controls](../../docs/evidence/runner-native-budget-2026-09-06/summary.json)
exercise the unchanged 100,000-attempt runner bound. After obtaining an actual
child0/kind1 collected result, a private wrapper supplies local canonical pending
replies and counts synthetic yields without scheduling. Completion on the final
allowed attempt returns0, uses real EOF/closes and passes two generations with six
reclaims. Exhaustion returns1 with no further transport/output cleanup/policy
calls, verified by witness114. Private off-by-one mutants produce witness115 before
attempt100,001 reaches transport, or witness116 after only99,999 attempts. Negative
cases require exact child0/parent witness/owner970 with reclaimed0 and no success.

All 66 combined native cases, nine legacy cases and affected host regressions pass;
all 57 prior client ELFs remain identical. The first attempt passed. This is Aether
execution of runner control flow with injected replies/yield observation, not
100,000 remote pending exchanges, stuck-child scheduling, a time deadline or
unknown-resource recovery. Production behavior and all producer/SDK pins remain
unchanged. Current relevant owner contract/broker/backend hashes still match the
consumed producer; local help/error output needs the proposed owner extension.

Next local work: plan host local-outcome delivery and cleanup controls against the
proposed output fixtures. Native local outcomes, unknown-resource recovery and
independent reviews remain open. UL-059 stays active; UL-069 remains deferred.

Add `--budget-controls` to the previous full carrier/uncertainty command for all
66 cases. The flag implies mapped producer/build support; alone it selects 26
cases (nine legacy, 13 mapped, four budget). Existing process and guest limits
apply. `budget-native.c` wraps exchange, channel/yield, read, close and terminal
policy; private short/overrun directories contain only test runner/header copies.
Actual prefetch exchange/yields stay bounded and separate from synthetic attempts.

## Four-role producer integration in progress — 2026-09-07

The newer runner handoff is being consumed separately from existing profiles.
[Four-role preparation](../../docs/evidence/four-role-consumer-2026-09-07/README.md)
passes648 host decoder controls and links an independent native parent using the
real startup selector/result policy. The231-file SDK matches. Native execution is
NOT RUN; the next gate is a source-rebuilt owner/backend/child boot and exact output/
status/reclaim verification. Run prepare-four-role.py for preparation only; its
parent ELF must not be used with the legacy two-binding producer.

## Four-role native checkpoint — 2026-09-07

[Independent native execution](../../docs/evidence/four-role-native-2026-09-07/README.md)
now passes the command-success path: real parsed startup, source-built bytecount,
independent exact output/status verification and six native reclaims across two
generations. Private wrong-role and omitted-close controls reject at1401/1403.
Run `python3 -B experiments/command-runner/run-four-role.py` with the exact inputs
documented there. The initial build-environment failure is retained. Public local
outcomes and full UL-059 acceptance remain open. Next roadmap work is the newer
UL-067 real-cat delivery, followed by native dash command/pipeline integration.
