# Owner-local live workers

Status: private producer qualification passes, 2026-10-04.
[Before-code scope](contract.md) selects 82 live service records and two per small
owner with existing lifetime, authority and memory bounds.
[Park/wake extension scope](park-contract.md) qualifies the actual full context
list through indefinite waits and counted wake.
[Reference](../../NATIVE-SERVICE-WORKERS.md) records remaining limits.

201 fresh target cases pass: 162 maintained memory/thread, 14 origin/reuse/entropy,
seven M4, ten larger-owner memory, two ordinary storage, three worker capacity/
stop/rebind and two park/wake/stop, plus one unsupported envelope. Full 137 Python/
Zig/Rust/pin/workflow and eleven build guards pass. Compiled geometry binds
64,288 service-child bytes and 4,704 small-child bytes at 784/alignment16 per
record, with a 672-byte temporary context-list bound. No stack-peak claim.

The first source transform's final audit matched legitimate child element-address
expressions and failed before writing native_c; no target ran. The first capacity
guest passes, but the stop helper lacked its per-case macro, exited normally and
the supervisor correctly rejected it. All failed source/packet/commands/logs/ELF/
ISO remain. Final worker cases ran fresh after fixing fixture compilation. Actual
omitted reset rebind fails262. Stop emits no serial terminal row; the compiled
supervisor must observe (144,3), then three successful reclaims and replacement.

`sdk-setup.py` stages verified offline inputs; `threads.py` runs the new capacity/
stop/control; `park.py` exercises all parked/wake and stop/replacement. `geometry.py`
binds actual linked storage. `regressions.py` runs maintained embedded/external
memory and default/large pair/pthread matrices. Origin/reuse/entropy and memory/
storage regression recipes preserve their existing consumers. M4 uses
`python3 scripts/regression.py`. `guards.py` verifies prerequisites, four release
omissions and unsupported envelope rejection. `checks.py` binds all results and
offline format/pin/workflow; `archive.py` reads every owned member before deleting
verified duplicates. `manifest.json` binds this packet. Qualified worker snapshots
retain every original packet input, independently of later narrative updates.

82 is a host lower-bound trial, with bare FS cookies and requested stack sizes;
full native musl TCB/stack/allocation demand, identity/configuration/feature
closure, engine startup/fini/restart, reader/SDK and filesystem/package/R1 remain.
No sibling, public ABI, SDK adoption or released pin change.
