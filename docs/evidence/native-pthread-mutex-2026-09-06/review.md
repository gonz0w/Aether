# Scoped self-review

Independent review and companion acceptance remain outstanding.

- Verified musl source already used by the lifecycle adapter supplies four new
  mutex objects. No upstream source patch is introduced for mutex behavior.
- The public normal mutex and its internal timedlock fallback use the existing
  compare/wait/wake adapter with current thread authority. No lock no-op or
  ambient native authority is introduced. The tested wait has no deadline.
- Parent holds the mutex before releasing the child. Atomic test observations
  record attempted entry and a wait call on the actual mutex word. The protected
  counter changes only under the mutex in the positive fixture. Unlock releases
  the child; join and retirement precede the next cycle.
- The deliberately broken child skips locking and must fail exactly at 242.
  A generic kernel panic, watchdog timeout or missing runner is not acceptance.
- Parent coordination yields are counted toward the unchanged 64-yield protocol.
  At most eight are allowed per cycle, leaving a bounded final remainder.
- No kernel, native ABI, admission budget, dependencies, sibling or pin changed.
  Full thread regression is selected; memory/image/M4 evidence is reused only
  after verifying kernel/build hashes against native-pthread-reuse qualification.
- Only normal process-private, untimed contention is qualified. Multiple children,
  condition variables, timed/robust/PI/process-shared behavior and fairness remain
  outside this witness. It does not establish production libzpool integration.
