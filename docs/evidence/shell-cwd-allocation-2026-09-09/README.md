# Directory aliases and local allocation failure

All 344 command cases and host/pin/workflow checks (98 Python tests) pass on frozen
runtime inputs. Two new alias cases substitute stdout/stderr references for the
directory grant; each rejects client110 with unpublished startup state and four
reclaims. The existing stdin-alias case also passes, covering each stream binding.

A separately compiled fixture forces the first eligible getcwd(NULL,0) allocation
to return NULL without changing the allocator. The client resets errno to77 and
requires ENOMEM, restored native mask and an unpoisoned, admitted connection.
The next real allocation/free and ordinary generated init/copy/cleanup succeed in
both generations, with four reclaims. This tests local allocation-failure handling,
not kernel-wide heap exhaustion or all allocator failure modes.

The fourth new case omits ENOMEM assignment. Client106/owner1501 rejects the mutant
before reclamation; this is semantic detection, not cleanup qualification for a
broken adapter. Other cases preserve existing exact output and terminal oracles.
The one failure-selection counter is fixture-local and resets with worker reuse.

No failed or interrupted attempts occurred. The collector verifies predecessor
packet bytes, final runtime hashes and simplicity snapshot, then reads back every
archived source/target member. qualification.json identifies the run; manifest.json
seals this packet recursively. No normal allocator behavior, kernel, sibling, SDK
default, released pin or upstream object changed. No fresh M4 selection for this
fixture/mutation work. Rust edition2024 and existing local C style are retained.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-allocation-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#directory-alias-and-allocation-failure-selection--2026-09-09).
Next: the five metadata observations in the intake table, then matching consumer
reproduction. Full-main secure ENV, exec/wait and persistent filesystem remain
separate work. This result does not extend consuming-project acceptance or claim
complete POSIX/stat behavior.
