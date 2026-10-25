
## Native compare-and-wait contract — 2026-09-06

Before implementation: extend only native-threads' existing domain grant with
bounded address-local wait/wake, needed for the engine's mutex/condition/join
runtime. Aether owns atomic compare/block, scheduling and cleanup; libc locking
policy remains userland-owned. No pthread compatibility, global futex table or
cross-domain wake is introduced. Existing thread creation limits remain.

- 0x28003 wait: rdi thread grant, rsi aligned writable 32-bit word, rdx expected
  u32, r10 relative timeout of 1..100 native PIT ticks, r8/r9 zero. Validate first;
  compare and publish blocking state with interrupts disabled. Mismatch returns
  -11 without registering. Wake returns 0; timeout returns -110. Completion rdx is
  elapsed native ticks, not wall-clock time. No implicit retry or spurious wake.
- 0x28004 wake: rdi grant, rsi same kind of word, rdx/r10/r8/r9 zero. Wake all
  matching contexts in this domain (at most two), returning the number woken.
  Wake does not modify the word. Userland atomically stores its predicate before
  wake and loops around wait. Wake with no registered match returns zero.
- Invalid/missing/foreign/stale grant returns -13; alignment/reserved/expected/
  timeout errors -22; invalid word mapping -14. Failed requests have no queue or
  memory side effects. The existing inspect opcode additionally returns rdx=1
  while the child is blocked, else zero, without changing its rax exit contract.

Each execution has one fixed wait record; blocked execution cannot issue another
operation. Domain identity/generation scopes its key, so equal virtual addresses
in another domain do not match. Pin the wait's four bytes against protect/unmap
until completion. CPU state, TLS and stack pins remain active while blocked.
Deadline completion wins at/after the deadline; ordinary wake earlier returns 0.
Thread clear-TID first writes zero, then wakes same-domain waiters on that word.
Stop removes both wait records without resuming either context before TID/mapping
cleanup. Reclaim/reset drops all old-generation wait state.

The scheduler excludes blocked contexts. If admitted domains exist but every
context is blocked, return to a dedicated kernel idle frame/16-KiB stack. A timer
interrupt there updates native ticks/deadlines and selects runnable user work;
it must not overwrite a blocked user frame or copy kernel state into user space.
Only the explicitly selected idle timer path accepts a kernel-mode interrupt;
other kernel traps retain fail-closed diagnostics. Idle uses kernel-only mappings,
no user authority, and the existing normalized interrupt frame. Kernel code remains
soft-float; user FP state is saved before idle and restored before user return.
The interrupt gate excludes concurrent compare/register/wake/teardown mutation;
these BSP-local semantics make no SMP futex claim. No heap or dependencies added.

Forbidden: lost wake between compare and registration, cross-domain wake,
unmapping a queued word, scheduling a blocked or stopped context, hidden success
on timeout, all-blocked panic, stale generation wake or kernel/user frame mixing.
Document the extension here and the memory pin in NATIVE-MEMORY; update existing
thread-suite inventory with --waits. New C uses the pinned Clang format and C11
atomics; preserve existing adapter and output protocols.

Select host wait-state tests (mismatch, expiry/tie, wake, reset), native both-memory
profiles (mismatch-before-wait, registered wake, join/TID clear, idle timeout,
wrong key/domain/grant, word pins, stop/replacement and parent exit while blocked),
and exact compare/pin mutants. Run old thread/memory/image suites and M4 regression
plus host/format checks on frozen inputs. Retain every attempt. General clocks,
indefinite waits, cancellation, richer thread pools, stack measurement, optimized
modes, independent consumer review and actual libc integration remain open.
