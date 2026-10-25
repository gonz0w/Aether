# Native child TLS and TID storage — 2026-09-06

The opt-in thread grant now admits a declared child TLS range and separate
parent-TID/clear-TID locations. Creation writes the child ID to the parent output;
the independent clear word is left unchanged until exit/stop clears it and wakes
waiters. The whole TLS range remains pinned while running or blocked, including
pages on either side of FS. The parent output has no lifetime pin.

The [exact contract](../../NATIVE-C.md#native-child-tls-and-tid-storage-contract--2026-09-06)
defines opcode 0x28006's copied 96-byte descriptor, opcode 0x28007's scoped identity
query, validation/errors, write ordering and authority. Existing creation modes,
memory quotas and one-child lifetime limit remain unchanged. IDs are bounded
labels reused after domain replacement, not capabilities or stable process IDs.
Set-FS on the new child cannot escape its declared TLS span; set_tid_address returns
its child ID while retaining validated clear-word replacement behavior.

## Verification

[Final results](final/results.json) retain exact commands, UTC boundaries and
hashes for [frozen sources](final/sources.tar.gz). All selected checks pass:

- Six new cases in each memory profile: positive, supervised replacement,
  descriptor/output aliasing, stop with a blocked child, guard fault with peer
  completion, and skipped TLS pin rejection at assertion 194.
- Twelve stack, twelve wait, fourteen older thread, 25 memory, nine image and
  seven M4 cases: 91 target cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks. The
  execution-reset test now checks clearing declared TLS storage too. Zig and
  pinned C formatting pass.

The native C parent verifies distinct creation/clear words, current identity,
foreign-grant/reserved-field denial, full descriptor validation, unmapped and
read-only TLS pages, invalid late parent-TID, and unchanged failure sentinels.
The alias case places the descriptor in the future return slot and the parent-TID
output over its argument field; the child must receive the original argument.
The parent unmaps its one-time output before waking the child. Protect and unmap
of all three declared TLS pages are denied while the child is blocked.

The child checks its identity and set_tid_address return, rejects an FS escape,
moves FS within its span and restores it, checks TLS contents, and exercises its
256-KiB stack and FP state across yields. Clear-TID changes from the caller's 99
to zero on exit, independently of the ID publication. The guard control requires
actual vector 14/error 4 and terminal status 142, with peer success. The pin mutant
must produce exact assertion 194 terminals; panic or timeout alone is insufficient.

## Retention and limits

The initial six-case suite passed. Review then moved TLS geometry checks ahead of
backing checks to give consistent -22 rejection for any out-of-span FS, and added
unmapped-FS and unaligned-parent-TID counterexamples. Both revisions are retained.
There were no failed host or target attempts in this change. No sources changed
during final qualification; hashes were checked again before archival.

`before.tar.gz`, `contract.md`, initial logs and all thirteen target directories
listed in `target-directories.json` are retained. `target-attempts.tar.gz` contains
their source snapshots, producer receipts, artifacts and raw results. Actual musl
1.2.6 construction/TLS/join sources and COPYRIGHT are in
`consumer-source-review.tar.gz`, identified by `review-inputs.json`.
`formatter.json` records post-format executable/config identity. `SHA256SUMS`
covers this packet. No sibling source, release or consumer pin changed.

The parent uses the supplied strict musl build; the child remains a freestanding
conformance fixture. This is not an actual pthread port or consumer acceptance.
Main-context TLS extent registration, signal/cancellation behavior, repeated
thread creation and measured engine resource budgets remain open. The native
OpenZFS/Rust service and assembled shell/package release remain unfinished.
Independent reader/consumer review, optimized modes, stack high-water and extended
stress evidence remain missing. Top-level UTC boundaries do not cover every
internal libc-builder command. Passing checks do not establish release readiness.
