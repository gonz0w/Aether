# Native child stack ranges — 2026-09-06

The existing opt-in thread grant now admits an explicit stack range and initial
RSP through opcode 0x28005. All pages must already be owned anonymous RW/NX
backing. The kernel copies the complete descriptor before writing outputs and
pins the whole stack while the child runs or blocks. Legacy one-page creation,
the one-child lifetime limit and memory quotas remain unchanged.

The [contract](../../NATIVE-C.md#native-child-stack-range-contract--2026-09-06)
records requirements, forbidden outcomes, owners, unsafe boundaries and selected
verification before implementation. Actual musl 1.2.6 sources use 128-KiB default
stacks with 8-KiB guards; the reviewed OpenZFS helper requests 256 KiB. Reviewed
source bytes and musl notices are in `consumer-source-review.tar.gz`, with hashes
in `review-inputs.json`. OpenZFS LICENSE and COPYRIGHT accompany this packet.
No upstream source or immutable consumer pin was changed.

## Results

[Final results](final/results.json) retain exact commands, UTC boundaries and
hashes for [frozen sources](final/sources.tar.gz). All selected checks pass:

- Six stack cases in each memory profile: positive, supervised replacement,
  overlapping descriptor/output, stop with a blocked child, guard fault with
  peer completion, and deliberate stack-pin bypass rejection at assertion 194.
- Twelve wait, fourteen older thread, 25 memory, nine image and seven M4 cases:
  79 target cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks,
  including a new pure stack-geometry test. Zig and pinned C formatting pass.

The native C fixture uses a 256-KiB stack with an offset initial RSP, preserves
metadata above it, touches a large local array, and checks every stack page's pin.
Malformed descriptors, invalid geometry, missing/incorrect backing and late TID
failure leave publication and output sentinels unchanged. The actual guard read
produces vector 14/error 4 and terminal status 142 while the peer completes.
Exit releases pins; forced stop and replacement reclaim the domain safely.
`child-disassembly.txt` records the final ELF's large stack reservation, with tool
and ELF hashes in `disassembly.json`; this is not a general high-water measurement.

## Retention and limits

The initial six-case stack run and all final suites pass. In the initial receipt,
the alias test used the historical producer key `parent-exit`; the final harness
names the case `alias-descriptor`. Both execute THREAD_ALIAS, not a parent-exit
test. This naming correction preceded the frozen final qualification. No inputs
changed during qualification, and their hashes were checked again before archival.
`before.tar.gz`, initial logs and all target directories in
`target-directories.json` are retained; `target-attempts.tar.gz` contains their
sources, producer receipts, artifacts and raw results. SHA256SUMS covers this packet.

Only the parent calls the existing pinned musl libc. The child is a freestanding
conformance fixture; actual pthread construction is not ported. Next work is libc
thread identity/TLS/lifecycle integration, followed by measured engine resource
budgets. Signal semantics, repeated thread creation and other documented libc
gaps remain. There is no native OpenZFS service or assembled shell/package release.
Independent reader/consumer review, optimized modes, stack high-water and extended
stress coverage remain open. Top-level UTC boundaries do not cover every internal
libc-builder command. These checks do not establish consumer acceptance or release
readiness.
