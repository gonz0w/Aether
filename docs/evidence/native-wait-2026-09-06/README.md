# Native compare/wait/wake — 2026-09-06

The opt-in thread grant now supports atomic compare-and-block and domain-local
wake, with a 1–100 native-tick timeout. A waiter keeps its CPU/TLS/FP state and
pins its wait word. Wake and timeout remove the registration; clear-TID writes
zero before waking a join waiter. Domain stop cancels both contexts' waits before
TID and mapping cleanup. Equal addresses in another domain grant no wake access.

When all admitted contexts are blocked, a dedicated kernel idle frame and 16-KiB
stack handle timer interrupts until a deadline makes user work runnable. Idle
interrupts never overwrite saved user frames. Ordinary kernel traps still fail
closed. This is BSP-only and does not provide POSIX clocks, indefinite waits or
libc pthread compatibility. The existing one-child-per-domain bound remains.

The exact opcode, pointer, timeout, return-value and ownership contract is in
[NATIVE-C](../../NATIVE-C.md#native-compare-and-wait-contract--2026-09-06).
[Final results](final/results.json) contain commands, UTC boundaries and hashes
for the [frozen inputs](final/sources.tar.gz). All selected checks pass:

- Six wait cases in each memory profile: positive, supervised replacement,
  parent exit with a blocked child, forced stop/replacement of a blocked domain,
  deliberately skipped comparison, and deliberately skipped wait-word pin.
- Fourteen existing thread cases, 25 memory cases, nine large-image cases and
  seven two-core/framebuffer regressions: 67 target cases in total including waits.
- 97 Python tests plus kernel and offline standards/workflow checks, including
  two new Zig wait-state tests and the new idle-evidence oracle test.
- Changed Zig and the C thread/wait fixtures pass pinned formatting checks.

The native parent verifies wake-before-wait/value mismatch, malformed pointers,
reserved fields, timeout bounds, foreign and old-generation grants, a timed wait
with elapsed ticks, a registered matching wake and wrong-key rejection. Blocked
wait words cannot be protected or unmapped. Join observes clear-TID and retained
child status. The old registration cannot wake a replacement: its initial key
is zero and its pre-registration wake returns zero. Shared coordination uses C11
atomics; only the parent calls the actual pinned native musl libc.

The unsupervised positive must show nonzero `NATIVE WAIT idle ticks=N` and both
successful terminal/output summaries. Each parent checks a distinct XMM0 value
across its idle timeout; TLS and FP remain checked across subsequent context
switches. Wake-before-registration cannot be lost because the changed word
returns -11. Host tests additionally exercise matching/nonmatching keys,
registration occupancy, timeout/wake ties, invalid bounds and reset cancellation.
The compare mutant fails at assertion 215 in both domains; the pin mutant at 218.
A generic panic or timeout cannot substitute for those exact terminal records.

## Retention and failures

The first host and target attempts failed during compilation: the wait result
needed an explicit named struct type, and an idle diagnostic variable shadowed
an existing local. No QEMU target ran in that attempt. Both errors were fixed;
the initial six-case wait suite then passed. The fixture was strengthened with
store-before-wait, a prior-generation grant and explicit FP-over-idle checks
before the full final qualification. No sources changed during the final run.
[The triage record](triage.json) distinguishes these attempts.

`before.tar.gz`, `contract.md`, raw logs and the failed target's source archive
retain the initial inputs. `target-attempts.tar.gz` contains every target directory
in [the inventory](target-directories.json), including the failed build and both
passing revisions. Producer receipts bind the supplied strict musl archive,
compiler/linker pins and ELF/envelope bytes. [Formatter identity](formatter.json)
records the tool/config digests. `SHA256SUMS` covers the whole retained packet.
No sibling source, standards release or consumer pin changed.

## Remaining work

Review the actual libc thread-construction requirements against this seam, then
qualify consumer integration and measured stack/TLS/thread-pool budgets for the
filesystem engine. A one-page child stack, one child per domain lifetime and
bounded native-tick waits are experimental limits, not an OpenZFS runtime budget.
The native engine/Rust filesystem service and assembled shell/package release
remain unfinished.

Independent reader/consumer review, optimized target modes, stack-high-water,
extended stress and full release qualification remain open. The wrapper records
top-level UTC boundaries; inherited libc builders do not record every internal
command boundary. Passing checks do not establish consumer sign-off, complete
draft-standard adoption or release readiness.
