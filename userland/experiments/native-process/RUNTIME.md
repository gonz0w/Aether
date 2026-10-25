# Independent broker execution (UL-046)

Six native cases pass with the independently authored C requester, producer Rust
broker/namespace and producer worker. The requester uses seven-byte requests and
five-byte replies, validates zero reply fields, treats tickets as opaque, and
checks request/response endpoint cleanup. This adopts the bounded connection-bound
launch/collect fixture, not POSIX fork/exec/waitpid or descriptor inheritance.

| Case | Retained outcome |
| --- | --- |
| positive | Worker slot 1 generations 1/2 exit 17/33; requester slot 0 exits 29; supervisor 100/reclaimed 3; existing file-service pass marker |
| allow-inheritance | Independent requester 51 rejects accepted nonzero inheritance; supervisor 903/reclaimed 2 |
| wide-scope | Requester 52 rejects access to the broker's wider requester executable binding; supervisor 903/reclaimed 2 |
| repeat-collect | Requester 66 rejects a second successful collection; supervisor 903/reclaimed 2 |
| partial-request | Requester 41 exits after four request bytes; broker rejects framing after requester reclaim, result 903/reclaimed 1 |
| requester-exit | Requester 42 exits after launch acknowledgement; broker cleans the remaining child and requester, result 903/reclaimed 2 |

All negatives require the exact requester status followed by the exact broker
result/reclaim count and profile-rejection panic; none may emit the pass marker.
Timeout, build error, boot error or generic panic cannot satisfy an oracle.
The positive case also checks denied direct launch, restricted/malformed names,
version/padding/field rejection, occupied child state, forged/stale tickets,
collection field validation and terminal kind/detail. A ticket is not a native
grant, parent PID, inherited file reference or recovery token.

## Producer pin and source drift

The first capture rejected a mismatch with the completed producer receipt before
compilation: Aether's checkout had newer `coexist` work. The final run restored
only receipt-matched bytes into a private kernel copy. Producer-retained sources
supply the broker, helper and owner runner; an earlier private native-stdio source
capture supplies the matching kernel/native-launch/build files. Every non-metadata
source entry in the completed producer report is verified. The receipt records
each restoration's donor/hash, the full final snapshot and all build commands.
No sibling working-tree source was overwritten or newer feature accepted by accident.

The initial UL-045 observation that no process evidence bundle was located is now
historical: the completed producer bundle was available for this run and its
summary/report identity was verified. The producer's six-case receipt remains
separate from these six independent consumer outcomes.

```sh
python3 experiments/native-process/check.py --aether ../aether \
  --restore-from build/native-stdio-files-454yqot3/Aether \
  --sdk build/native-c-xhkdw6jv
```

`--restore-from` supplies candidate bytes, never authority to accept a different
hash. A donor is used only when it matches the producer report exactly. Missing
matches reject. The requester is rebuilt through prepare.py against the previously
tested SDK inventory and tool pins. The broker uses the producer's fat-LTO/
one-codegen-unit recipe to preserve its 4 KiB immutable raw-code limit.
The runner retains image/envelope/serial identities, checks source/SDK stability
and uses the owner QEMU watchdog and terminal-marker parser.

[Evidence](../../docs/evidence/native-broker-userland-2026-09-05/summary.json)
retains all six cases, source restorations, producer/requester receipts, artifacts,
commands and serial logs. Unrelated file/libc/init/kernel suites were not rerun;
no shared adapter, kernel or init implementation changed in this task.

## Remaining work

Nonzero inheritance still returns ENOTSUP. The broker supplies fixed argv and no
file descriptors; it does not provide copied shell state, in-place executable
replacement, POSIX wait options, signals or recovery after lost replies. ABI-5
supervisor death remains fatal. The ABI-6 init profile and newer coexistence work
need their own consuming witnesses. This run does not test sys-init's SI-04
sequential cross-slot reuse failure or claim it fixed.

UL-047 subsequently consumed the completed process/file coexistence producer:
[six ABI 7 cases and six fresh ABI 5 regressions pass](COEXIST.md).
UL-049 also completed [six independent multi-client cases](CONNECTIONS.md);
UL-050 next consumes the distinct shared-files bootstrap fixture. The [published Aether roadmap additions](../../docs/AETHER-BACKLOG-FOLLOWONS.md)
cover inherited-file ownership/capacity and shell process semantics under the
still-pending canonical PD review. The user explicitly authorized publication after the initial automatic-review
rejection; UL-048 appended the exact entries to Aether’s roadmap. No blanket wait
or native shell acceptance follows from completing this broker witness.
