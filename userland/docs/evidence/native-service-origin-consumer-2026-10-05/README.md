# Independent worker-origin consumer

UL-003/015/081,2026-10-05. Complete13-file producer manifest and1512-entry
archive are verified before selecting final attempt2. Ten actual ISO payloads
bind exact ELF and supervisor. Ten fresh final native replays pass: joinable TSD,
worker reaper, concurrent/single worker-origin creation, descending cleanup,
stop/replacement, parent-only359, wrong-grant clone360, early-unmap352 and
omitted-primary-park356. Current3.14.7/minimum3.10.21 each reject50 corruptions.

Two service creators count within82 live workers and each creates40 detached
peers; the single-creator variant creates81. Actual musl's list lock serializes
publication on one vCPU; admission reads are atomic, callback identity follows
published native IDs, and distinct creator signal masks are retained/inherited.
Creation completes before cleanup. Primary pthread_join actually parks while a
charged ordinary creator reaps detached peers; confirmed stop precedes unmap and
retirement, and no unmapped TCB is read. Exact66/34 eager pages per mapping and2
retained allocator pages qualify this fixture. These are not engine high-water.

Positive cases require exact primary/peer/replacement identities, per-slot
ordering and supervisor100/reclaimed3. Stop uses the frozen supervisor's144/3
check and only two ordinary terminals. Denials require the primary's exact detail,
optional same-detail peer, supervisor401/reclaimed0 and a complete final panic.
The supervisor polls primary first and fail-stops immediately on rejection, so a
peer terminal can precede that receipt or remain unobserved. A consumer expectation
of both terminals failed on360; the original source/log/cleanup receipt remain in
the archive. The mutation that initially removed an optional peer was corrected
to remove the mandatory primary. No unrelated outcome is accepted as rejection.

Final harness review adds explicit interpreter pins and oracle digests to native
receipts. All ten cases rerun on those final bytes; prior passing runs remain
historical attempts. Both oracle interpreter runs bind final driver/checker bytes.
See finding.json, harness-review.json and [scope/review](source-review.md).

This is independent binary replay, not local source rebuilding or production SDK
adoption. Dynamic creation overlapping cleanup/reuse, multicore, production
reaper placement/resources, actual providers/identity/configuration and measured
engine startup/fini/restart remain open. Wider shell SESSION is separate;
SSDK-06/human reader remains deferred, full M3/R1/release unaccepted.

Reproduce offline from the repository root into a fresh owned build root:

```sh
python3 -B docs/evidence/native-service-origin-consumer-2026-10-05/prepare.py
python3 -B docs/evidence/native-service-origin-consumer-2026-10-05/run-final.py
python3 -B docs/evidence/native-service-origin-consumer-2026-10-05/check.py current
build/python-qualification/Python-3.10.21/python.exe -B docs/evidence/native-service-origin-consumer-2026-10-05/check.py minimum
```

Do not overwrite sealed packet records; copy the reviewed scripts to a fresh
packet destination first. Producer recipes are inert inputs, never executed.
QEMU11.1.1 pc-q35-11.1/TCG/qemu64/one CPU/256MiB/no NIC, fresh disposable UEFI
variables;35s guest/45s owned outer,1MiB UART/4MiB stderr/16MiB owner file limits.
Preflight tools finish before native groups. Forced teardown fails; all final
emulators/groups are reaped. Quality/syntax/whitespace pass. Original work BSD-2;
producer musl/OpenZFS notices preserved. Retention records full archive readback
before owned duplicate removal, with exact archive identity in retention.json.
