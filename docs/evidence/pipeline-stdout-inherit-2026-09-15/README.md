# Inherited pipeline stdout — 2026-09-15

The parent now receives and validates a generation-bound stdout grant before
creating pipes. FD1 participates in actual masked fork snapshots. The single
output owner validates the parent's holding and reserves one for each copied
child; copied descriptors alone cannot create authority. Live descriptor allocation
accounts for occupied FD1 while keeping the existing pipe binding layout.

Children mark stdout CLOEXEC except the final reader. Exec validates each full
before/after snapshot and commits output holding removal before replacement
publication. Only the last replacement retains FD1; its subsequent description
reports that retained holding instead of granting new authority. Parent explicitly
closes its own stdout before pipe dispatch without closing the final child's copy.
The final child uses musl write/close, and the owner independently checks exact
pipe data newline and that all four output holdings are gone.

The writer still forges the same output reference after exec and must receive
EACCES, proving CLOEXEC removed owner authority as well as local descriptors.
The deliberate retain control leaves that writer holding alive: its forged write
is accepted, so the independent client rejects124 and the owner rejects2726 before
reclaim. This does not rely solely on a descriptor-table comparison.

## Qualification

Commands:

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

All38 native cases pass on final sources; target case total is102.524 seconds.
Positive requires nine copies/replacements, exact pipe/output bytes, independent
parent closure and fifteen normal reclaims across three generations. Retained
writer authority rejects child124 then owner2726 before reclaim. Host run returns0
with104 checks. No failed attempts occurred; intentional rejection evidence remains.
Exact commands, pinned tools/SDK, sources, timestamps, native artifacts and serial
hashes are retained. Kernel mapping remains8007680 bytes.

## Compatibility and limits

279 frozen runtime inputs; seven private capacity files change.47/50 earlier
ELF/raw images are byte-identical. Only the three earlier stdout-owner variants
change and are requalified; all old clients remain identical. Both new owners are
14536 bytes within16384. No kernel/shared pipe core or adapter/SDK/dependency/
quota/sibling/released pin change. Output remains32 bytes with16-byte requests.

Four generation-local holding bits are the authoritative output ownership state,
passed through staging, exec and dispatch. Existing descriptor counts validate
aliases; no global table or second FD ledger is added. Invalid staged/exec plans
fail before native copy/publication. Failure recovery during partial staging and
arbitrary lost-receipt schedules are not newly qualified. References are data;
authenticated channels and observed native lifetimes delimit authority.

This step covers inherited stdout only, with in-memory capture. Inherited stdin
and stderr, actual dash child-driven builtin/exec scheduling, console integration,
concurrent blocking wait/data scheduling and signal interruption remain open.
Unchanged pipeline/early-reader scripts, SIGPIPE/status composition, matching full
suites and independent SDK/userland intake remain required. Persistence/OpenZFS,
packages, recovery and sys-init assembly remain R1 work. No full-dash/release claim.

Preimplementation review and outcome are in NATIVE-SHELL-STARTUP. Review/source
archives preserve local guidance and test support. collect.py verifies all owned
output files against an archive before duplicate cleanup; cleanup.json records it.
Existing sealed packets are untouched. SHA256SUMS covers every packet file except
itself. Final checks bind Rust1.98 edition2024, Clang-format21.1.8, all offline pins,
simplicity snapshot, workflow, whitespace and unchanged frozen inputs.
