# Independent launch-broker requester preparation (UL-045)

Three requester ELFs compile and pass structural inspection against the pinned
strict-musl SDK. UL-046 now has [six passing native cases](RUNTIME.md). The following preparation
record describes the earlier compile-only checkpoint for its independent
consumer of Aether's new [broker source contract](../../../aether/docs/NATIVE-PROCESS.md).
The [integration refresh](../../docs/NATIVE-DASH-GAPS.md) identifies what this
broker does and does not provide for dash.

The [requester](requester.c) uses independently authored framing: seven-byte
writes and five-byte reads over the delegated channel pair. It receives argc=1,
argv[0]=requester and auxv input/output endpoints. Unlike the file protocol, the
broker sends no initial root reply. The requester treats tickets as opaque;
no ticket value is translated into a PID or native grant.

| Prepared artifact / future case | Intended oracle; not yet executed |
| --- | --- |
| requester.elf / positive | Denied direct launch, unsupported inheritance, namespace/version/field/padding denial; two worker launches and collections; occupied record, forged/stale/repeated collection denial; details 17 then 33, kind 1; request close and reply EOF; requester 29, supervisor 100/reclaimed 3 |
| requester.elf / allow_inherit broker cfg | Inheritance refusal assertion 51; owner broker rejection 903 with owned cleanup |
| requester.elf / wide_scope broker cfg | Restricted-name assertion 52; owner broker rejection 903 with owned cleanup |
| requester.elf / repeat_collect broker cfg | Repeated-collection assertion 66; owner broker rejection 903 with owned cleanup |
| partial.elf / normal broker | Four-byte partial request, requester 41; broker rejects incomplete frame after cleanup |
| early-exit.elf / normal broker | Requester 42 after launch acknowledgement; broker stops/reclaims remaining worker before rejecting incomplete workload |

The [runtime results](RUNTIME.md) now establish the exact terminal ordering and
reclaim counts. The preparation plan required UL-046 to determine them from
the consumed producer snapshot. The owner runner's current expectations are
903/reclaimed 2 for its policy controls and early exit, and 903/reclaimed 1 for
partial input. Those are producer expectations, not results for this requester.
Boot failure, timeout or generic panic cannot pass any consumer case.

```sh
python3 experiments/native-process/prepare.py --sdk build/native-c-xhkdw6jv
```

The preparation verifies SDK contents against UL-044's retained libc receipt,
pinned compiler tools, explicit musl linkage, no unresolved symbols or Linux
syscall instructions, ET_EXEC/x86-64, bounded TLS/size, NX stack and no dynamic
or W+X segments. This is not full native loader validation. Outputs stay under
build; the script does not build the broker, launch a VM, install anything or
change a companion source. [Build evidence](../../docs/evidence/native-dash-gaps-2026-09-05/summary.json)
retains the three ELFs and their source/tool/input identities.

This uses AENFS001 / ABI 5 as a connection/launch conformance fixture. It is not
POSIX fork, exec, waitpid or descriptor inheritance, and it does not combine the
separate file-service and ABI-6 init profiles. Lost replies remain ambiguous;
there is no mutation replay or reconnect. Shared PD owner review remains pending.

UL-047 adds [six native ABI 7 coexistence cases and six ABI 5 regressions](COEXIST.md).
`prepare.py --coexist` builds the routed-file requester; its default remains ABI 5.

UL-049 adds [six independent ABI 9 multi-client transport cases](CONNECTIONS.md).
The separate connections-prepare.py builds both client roles without changing the ABI 5/7 requester.

UL-050 adds [six fixed-alias shared-file cases](SHARED.md), with independent clients
for both exit orders and explicit rights/position/final-close controls.

UL-051 adds [nine independent admission/collection cases](INHERITED.md), including
explicit rejected-admission retries and one-time child-result collection.

UL-053 adds [fourteen bounded inherited musl read/close cases](INHERITED-LIBC.md),
including whole-connection poisoning and no-replay controls.

UL-054/055 consume the delivered [bounded file-I/O extension](FILEIO-LIBC.md): ten
native cases cover real musl short reads/writes, EOF, capacity and reply failures.
