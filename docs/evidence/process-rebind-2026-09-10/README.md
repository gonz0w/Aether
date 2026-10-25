# Local libc child rebinding — 2026-09-10

The local raw-connection hook now refreshes the child's known auxv grants,
endpoint variables and pthread TID after validating its explicit fresh grants.
It uses private headers extracted from the existing receipt-pinned musl 1.2.6
archive, including its COPYRIGHT; no sibling implementation or released pin is
modified. See the [pre-code selection and scope](../../NATIVE-SHELL-STARTUP.md#local-child-rebinding-witness-selection--2026-09-10).

All 22 connection cases and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. Public getauxval/gettid and mmap/mprotect/munmap use the
child's updated stores; explicit endpoint traffic continues after rebinding.
Parent stores remain unchanged across two generations and six reclaims. Old
memory authority and reversed endpoint roles reject without cache writes.
Omitting auxv, TID or endpoint updates must reject child240/241/242 respectively,
owner1820 and zero reclaims. Older controls preserve their exact required outcomes.

This fixture stops outside library operations with single-thread locking disabled
and a zero thread-list lock. It is not a public fork wrapper, SDK-owner adoption,
arbitrary lock/atfork recovery or inherited command descriptor implementation.
Malformed auxv is bounded to the loader's 15 pairs plus terminator; the hook only
accesses the known libc pointer, never scans arbitrary process memory for grants.
Kernel authority still comes from checked grants, not stored integers or TIDs.

The first compatibility audit compared entire envelopes and failed because the
harness generates fresh bootstrap entropy. comparison-attempt-1.txt retains that
failure. The corrected comparison verifies original report hashes and compares
all bytes except the exact entropy interval [32,80). All 18 prior cases match.
No target attempt failed. Kernel and build source hashes are unchanged; the new
helper and harness branch are connections-only. M4 and the 431-command suite were
not rerun; their earlier packet remains historical evidence, not fresh coverage.

Each selected run retains exact command, UTC start/end, monotonic elapsed time
and exit status. Reports and archives bind sources, tools, extracted private
headers and target artifacts. Formatting, Python syntax, the simplicity snapshot,
workflow and standards checks have separate receipts. The collector validates
final sources, previous packet integrity, the exact source delta and archive
readback. The final manifest binds this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Next: command transport binding/descriptor state and SDK integration, inherited
open descriptions, transactional exec/CLOEXEC and wait. Signal/thread-copy
composition, unchanged DASH-argv, independent owner acceptance, extended testing
and assembled release readiness remain open.

Archive readback verified 223 frozen source files and 529 target artifacts,
including the extracted musl headers and COPYRIGHT. The comparison audit failure
has no separate outer timing receipt; all selected host/target runs do.
