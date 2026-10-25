# Fresh AF07 preparation —2026-10-23

Status: offline inputs and two qualification images prepared; fresh native
changed-composition disposition pending. No guest ran. This is not a persistent
shell, Zsh/TTY, package, ISO acceptance or independent review.
[Compact results](results.json) retain commands, hashes, scoped failures and
superseded preparations; [review](../../reviews/2026-10-23-af07-inputs.md) and
[procedure](../../../sys-init/docs/decisions/0214-fresh-af07-inputs.md) define scope.

The prior e002 expectation was wrong: actual SESSION r9 selects image c003.
Corrected consumer and actual kernel-frame-to-Rust negative/positive checks pass
before any native attempt. Event operations keep their separate e002 selector.
Old evidence and seals remain unchanged. Fresh compilation resolves the four
previously stale AF07 tests without disabling live-source checks or rewriting
historical manifests. Released standards pins remain exact.

| Active input | Manifest SHA256 |
| --- | --- |
| `.deps/fs-launch-af07-2026-10-23-v6` | `66e51e07ec9c8a512542c7dc6c606d5fb9d4af3ad8b7f951596ced53d42074c6` |
| `.deps/fs-init-af07-2026-10-23-v2` | `831e434721c933a64aa34beda139d3950c6516d1e8dd0124fc57166677f3e11a` |
| `.deps/fs-owner-af07-2026-10-23-v1` | `db1a489dd2117482502791a143cb911f2a570973263c17140b93ea07eed6d158` |

Engine ELF reproduces `9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a`;
ABI29 activation reproduces2072 code/1096 inspected stack. Fresh ABI31 owner
measures39376/49152 code,3408+4096=7504/8192 data and8000/8184 conservative stack.
Full actual shell/helper links, enforcing parser and selected Debug kernel pass.
Same35MiB/seven domains/twelve channels and all authority limits remain fixed.

Final focused checks:4 stack/entry methods,25 AF07/intake/selection/workflow,
12 adjacent data/constant-edge/metadata-session methods,6 component qualifier
methods:47 total, all pass. Workflow, three offline standards pins, component
quality and static checks pass. The qualifier tests actual intake/parser and
wrong closure/bounds, exact/omitted/duplicate/reordered results, balanced storage
waits, identity and failure-stop orchestration, unknown-stop resource retention,
CLI rejection and real host-child serial/panic/EOF/watchdog/reap. These are host
checks, not native fault, scheduling or cleanup evidence. The broad suite was
not rerun; the previous broad checkpoint is not promoted to a new full-suite pass.

Two initial host-fixture failures are retained in results: incomplete extracted
frame scaffold and macOS /var vs /private temporary-path expectation. Both were
fixed in test scaffolding; production checks were not weakened. Two offline image
preparations were superseded by stronger dependency/process/oracle checking, with
no guest. Their hashes survive, generated outputs were removed.

Pending qualification directory:
`zig-out/thread-suite-service-runtime-zpl-pair-fs-session-owner31-2_d4s5m0`.
Prepared `results.json` SHA256:
`c71661204daa1291e35c3bc983792e060405e4c301854133ce124884f23643ca`.
Final freeze verifies573 paths,6458 original pinned reader files,344 reader-runtime
files, exact emulator/firmware and both ISO hashes. Exactly two pending ISOs and
the prepared receipt remain as active inputs; copied source/SDK/object trees are
removed. Dependencies are retained separately, not copied into evidence.

Proposed single diagnostic: pristine READ-only original-file reader → guarded
owner running the fixed serial immutable-helper exec/wait script → fresh original
file recovery only after clean writer success. It issues zero filesystem mutation
requests; import/export can write metadata. Existing9-mutation/96-request storage
qualification remains separate. Writer60s/6000 ticks, readers30s/3000, normalized
capture64KiB and every current resource/authority limit stay fixed. Exact helper7,
parent0, engine0, admissions,21 cleanup rows, ordered/balanced waits, bounded halt
and full original-file/media recovery are required. Stop on the first unexpected
outcome, no retry. Unknown emulator stop retains resources. A confirmed final stop
removes generated images/media and keeps compact results.

After the required fresh human disposition, the prepared command is:

```
python3 -B sys-init/scripts/qualify-af07-owner.py --run --prepared /Users/cam/DEV/Aether/zig-out/thread-suite-service-runtime-zpl-pair-fs-session-owner31-2_d4s5m0 --prepared-sha256 c71661204daa1291e35c3bc983792e060405e4c301854133ce124884f23643ca
```

The existing rule is in OPENZFS-FEASIBILITY, “Required independent disposition”:
“Changed relevant runtime inputs require fresh review; this acceptance does not
carry automatically to another runtime composition.” Consumed one-sequence
approvals do not authorize this new ABI31 composition. Persistent executable loading,
public writable paths, continued-parent/failure qualification, packages and Zsh/TTY/
usable ISO remain R1 work after this diagnostic; no milestone is closed by preparation.
