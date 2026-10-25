# Native taskq object qualification — 2026-09-06

The [stage contract](contract.md) and [native contract](../../NATIVE-TASKQ.md)
limit this result to x86_64 musl objects and a relocatable link. No runnable
executable or QEMU acceptance is claimed. No kernel, sibling or pin changes are
needed for this stage.

## Results and attempts

| Attempt | Outcome |
| --- | --- |
| 1 | Compile, layout, relocatable link, negative controls, formatting and host tests passed. Review then corrected the retained upstream hz constant from 100 to 119. |
| 2 | Compile, layout, link and host tests passed; the corrected header failed clang-format. Preserved, not accepted as final. |
| 3 | Corrected formatting, complete upstream license/copyright, source/header inventory freeze and musl export checks all pass. Final accepted object stage. |

Each attempt retains its results JSON, top-level log and artifact archive with
compiler logs, original/adapted source, objects, negative inputs and source snapshot.
The source prefix is byte-identical to the pinned taskq.c; the appended TSD helper
and derived header are explicit adaptations. Input and tool digests are in results.
Attempt 3 also hashes its runner and rejects added/removed source or SDK header files.

Native layout in bytes: taskq 384, entry 40, mutex 48, rwlock 72, condition 48.
The proposed arena remains eight 512-byte slots in one 4096-byte mapping.
The copied one-byte queue limit rejects at `taskq exceeds arena slot`; an injected
import rejects at `unreviewed native import`. Both are deliberate controls.

The relocatable object retains 31 imports: 24 exports verified in the pinned musl
archive and seven unimplemented integration hooks (parent authority, arena map/
unmap, worker start, reaping, wait observation and fatal failure). Archive exports
are not transitive native syscall closure. Required allocation/clock failures,
concurrency, resource recovery and two-generation execution still need native tests.
The final host run passes 98 Python tests plus Zig and offline pin/inventory checks.

## Reproduction

From the repository root, use the exact local LLVM/musl SDK and retained OpenZFS
archive identified by `build.py` and the results. Select a fresh attempt directory
in a copied runner; existing attempt directories deliberately reject reuse. Run:

```sh
python3 docs/evidence/native-taskq-build-2026-09-06/build.py
```

This is a retained local recipe, not a portable SDK builder. It reads the sibling
SDK without modifying it. Keep sources frozen during the run; preserve every
failure. Runtime hooks must be implemented before the contract's paired lifecycle
acceptance can run. No production filesystem or release readiness follows here.
