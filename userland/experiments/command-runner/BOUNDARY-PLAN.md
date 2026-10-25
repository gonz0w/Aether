# UL-058 command adapter boundary plan

2026-09-06. Test design on the reviewed two-binding native-io.c; all cases below
are NOT RUN as new UL-058 tests. Existing UL-057 runtime evidence remains separate.
Apply CC/CP, TD/TE, Foundations O/I/E and the local Distribution applicability map.
No new native API, grant, global FD table or sibling implementation is authorized.

## First slice: host adapter controls

Compile the actual native-io.c with pinned Clang/C17 and host address/undefined
behavior instrumentation where supported. Supply test-only getauxval, channel_raw
and channel_yield at link time; do not copy the adapter implementation into a
model. Run each scenario in a fresh owned process so globals/TLS begin naturally;
no production reset API or include-source access to private state. Observe public
__aether_io, native_ref, native_bootstrap and native_exchange plus a scripted peer's
exact call/byte counters. Host seams do not prove native authority or remote cleanup.

| ID | Stimulus | Required independent observation |
| --- | --- | --- |
| CB-01 | Valid parent/child pair, generations 1/2 | Both references match; allowed I/O goes to exact channel and frame; wrong rights reject without traffic |
| CB-02 | Valid first entry, bad second reference/FD/rights, each separately | Bootstrap fails; neither binding live; read sentinel unchanged; I/O/close EBADF and zero further transport |
| CB-03 | Bad first entry, nonzero status/trailer, invalid generation | Same no-publication oracle; all pair validation failures remain failures |
| CB-04 | Missing/equal input/output channel | Startup fails without channel I/O; no descriptors exposed |
| CB-05 | Bootstrap prefixes 0/1/4/16/31 then EOF/error | Failure with neither binding live; no second read attempt after fatal outcome |
| CB-06 | Successful bootstrap followed by bootstrap again | Second call fails without additional transport; existing bindings remain usable |
| CB-07 | Failed bootstrap followed by bootstrap/exchange attempt | No implicit retry or launch; record actual traffic and poison state limits; a current failure is a defect to fix, not an expected pass |
| CB-08 | Short transfers and EAGAIN then progress | Exact total frame, no duplicate prefix; yielding does not alter bytes |
| CB-09 | Zero, overlong result, fatal error or EAGAIN budget exhaustion | Poisoned connection; bounded calls; no later exchange/file traffic |
| CB-10 | Dropped/malformed read reply after peer completion | EIO; destination untouched; subsequent file/launch/collection exchange makes zero calls |
| CB-11 | Dropped/malformed close reply | Local binding consumed once; second close EBADF; connection cannot replay |
| CB-12 | Reply padding/nonzero metadata, result outside range, negative close | EIO and poison; no caller-data copy; raw signed error domain tested |
| CB-13 | Exchange sizes other than 32/384 | No frame emitted, connection poisoned; all subsequent exchanges rejected |
| CB-14 | Early-publication and disabled-poison mutations in disposable source copies | Controls fail at the specific sentinel/binding/traffic oracle; generic build failure or timeout cannot count |

CB-07 is a source-observed concern: malformed complete bootstrap returns false
without setting poisoned, and missing-channel cases can leave fields zero. The
finite entry currently exits immediately, but public lifecycle must not assume
that caller behavior. Determine whether all failed initialization attempts must
be terminal; correct under a separate reviewed change if the control exposes
transport after failure. Never weaken the negative oracle to fit current code.

## Native follow-on slices

Use the separately locked producer bundle in docs/RUNNER-INTEGRATION.md only in a
new opt-in consumer. Preserve the existing driver/pin and nine native regressions.

- NB-01: malformed second binding and early-publication mutation, observing actual
  musl read/write/close, sentinel and channel counters before a deliberate terminal
  rejection. Require exact child/parent/broker markers. No remote recovery claim.
- NB-02: dropped read, malformed read and lost close after real service completion;
  no subsequent file, launch or consuming collection traffic. False-poison control
  must be rejected. Retain observed side effects separately from unknown replies.
- NB-03: complete malformed 384-byte frames, exact errno/zero receipt and successful
  aligned follow-on; partial prefixes 0/1/4/16/31/32/383 require exact producer EOF
  rejection and no admitted child. Keep live-parent and parent-exit race distinct.
- NB-04: actual abnormal child and same numeric normal status, one-time collection,
  independent backend bytes and explicit reclaims. Host synthetic stop/wide-detail
  checks cannot be labelled native kernel witnesses.

## Execution, evidence and completion

Owner: Aether-userland maintainer; implementation/technical review in this task,
independent technical and reader review pending. Record a case manifest before
coding with exact expected errno, counters, status and mutation rejection. Use
process.py, private build roots, clean environments and pinned tools/SDK. Host
case deadline 30 seconds, build 180 seconds; bounded native guest watchdog
30 seconds and 15-minute suite budget. Record compiler flags, sanitizer runtime
identity, source/plan hashes, per-command cleanup and every attempt. A missing
instrumentation/runtime dependency leaves that stage NOT RUN, never green.

Run host controls plus the existing 21 command cases. Adapter changes require
fresh five-ELF inspection and all nine native regressions; widened native cases
require exact producer/consumer builds and their semantic controls. Run
python3 -B docs/quality/check.py. Preserve logs and failures without automatic
pruning. Partial stream/unknown outcome is not reconnect or recovery acceptance.
UL-058 completes only with independent native boundaries and unresolved follow-ons
recorded; this plan alone does not close it or UL-059.

## First host checkpoint — 2026-09-06

CB-01–07 now have 22 scoped host scenarios: four valid role/generation pairs,
eight corrupted bootstrap words, invalid generation, four channel configurations
and five EOF prefixes. Two CB-14 mutants prove the reference-publication and
poison traffic oracles. The original adapter fails 13 scenarios; the corrected
one passes all 22 with UBSan, preserving successful re-entry. Missing/equal and
malformed startup are now terminal attempts with poisoned transport. No native
failure injection is claimed by the nine passing legacy regressions.

Reproduce: python3 -B experiments/command-runner/check-bootstrap.py
--sanitizer undefined --mutations (on one command line). Default instrumentation
remains address,undefined; ASan is incomplete in this host environment because
both the first adapter case and an empty main time out. UBSan-only selection is
explicit. [Evidence](../../docs/evidence/command-bootstrap-2026-09-06/README.md)
retains all failures and controls. CB-08–13, additional mutation coverage and
NB-01–04 remain NOT RUN; these checkpoints supersede the initial blanket status.

## Transfer/reply host checkpoint — 2026-09-06

CB-08–13 now have 53 scoped host scenarios plus two CB-14 mutations: short/EAGAIN,
exact retry budgets, zero/fatal/overlong results, reply padding/metadata and signed
result bounds, dropped/partial read, consuming close and forbidden frame sizes.
All pass with explicit UBSan; 24 bootstrap and 21 command regressions pass.
The adapter is unchanged. Initial validator-mutation compile failure is retained;
its corrected semantic rejection passes. [Evidence](../../docs/evidence/command-transfer-2026-09-06/README.md).

Run python3 -B experiments/command-runner/check-bootstrap.py --suite transfer
--sanitizer undefined --mutations on one command line. These tests capture full
requests but simulate missing replies; they do not prove native peer completion.
ASan remains incomplete. Next: NB-01–04 real transport/child boundaries and the
separately pinned UL-059 integration. Earlier NOT RUN wording is historical for
these scoped host cases; native witnesses and independent reviews remain open.

## NB-01 checkpoint — 2026-09-06

Three native second-binding corruptions and an early-publication mutation now
pass exact child/parent/broker rejection oracles. Real musl calls and the adapter's
channel-call wrapper verify nonpublication, sentinel preservation and no traffic
after failed bootstrap/re-entry/launch. See [native reproduction](NATIVE.md) and
[evidence](../../docs/evidence/native-bootstrap-userland-2026-09-06/README.md).
Original nine-case producer regression and 13 new-producer cases pass separately.
This completes the scoped NB-01 witness; native partial bootstrap and additional
field combinations are not exhaustively covered. NB-02–04 remain next work.

## NB-02 checkpoint — 2026-09-06

Lost/malformed read and lost close are now injected after receipt of complete
native service replies. Real musl and adapter channel counters verify sentinel,
errno, consuming close and no replay. The disabled-poison mutation is caught
before its first forbidden trap. Exact rejected-workload terminals are retained;
no remote recovery claim. [Evidence](../../docs/evidence/native-replies-userland-2026-09-06/README.md).
All 17 combined cases, nine original-pin and 21 host regressions pass. The ordinary
adapter and nine prior client ELF bytes are unchanged. NB-03/04 remain next.

## NB-03 checkpoint — 2026-09-06

The documented 22-field complete-frame corpus now rejects with exact errno/zero
receipt in both generations, then runs a valid aligned command with six reclaims.
Seven parent-live truncated prefixes require exact length-specific EOF rejection
and no terminals. Existing bad-version and pad-EOF producer mutations are caught
at specific parent/broker outcomes; no owner source mutation is carried locally.
[Evidence](../../docs/evidence/native-launch-userland-2026-09-06/README.md) records
all ten added cases, 27 combined passes, nine original and21 host regressions.
NB-03's scoped witness is complete; peer-exit races and recovery are separate.
Next: NB-04 native terminal kind and collection behavior, then UL-059 integration.

## NB-04 checkpoint — 2026-09-06

Normal exit134/kind1 and actual fault134/kind2 now have native consumer witnesses,
including abandoned child aliases, one-time collection, independent output checks
and six reclaims. Misreported kind is caught with exact child/parent/broker records.
[Evidence](../../docs/evidence/native-terminal-userland-2026-09-06/README.md)
records 30 combined native passes, nine original and 21 host regressions.
The finite parent still exits29; wide-detail/stop/unknown recovery are not promoted.
NB-01–04's scoped native work is complete, while independent reviews and full
public startup observation remain open. Proceed to UL-059 carrier/parser work.
