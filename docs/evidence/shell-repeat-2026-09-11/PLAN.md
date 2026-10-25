# Repeated external commands in one dash lifetime

Requirement: one actual serial dash parent launches /next three times, collecting
and reclaiming each child before reusing slot2. Parent slot0 generation1 and UART
backend slot1 generation1 remain alive. Exit0 closes the three streams; backend
shutdown and its generation2 denial probe complete six reclaims. No pool increase.

Separate parent generation, child generation and parent freeze sequence. Child
routes are validated against the current child generation, but refer to the same
backend descriptions/positions. Replacement bootstrap is addressed to the child;
its real getppid remains5. Reclaim requires terminal72, executed image, no pending
or partial request, all child holders released and a valid issued wait receipt
acknowledgment. Old child handles must be invalid after reclaim. No early reuse,
parent restart, backend reset, fabricated PID/status, stale token acceptance or
ambient UART authority is allowed. Bound three admissions and existing event loops.

Aether owns this private native conformance fixture. Userland owns independent SDK
and dash acceptance; sys-init owns supervision. No sibling changes, public ABI,
pins, source-built upstream object changes or post-R1 feature work are needed.
Existing candidates and older cases remain reproducible. SE-01–05: reuse the
existing dispatcher, holder table, channels and lifecycle operations; add only a
cohesive admission routine for repeated copies. No second process manager, global
table or optional future filesystem mechanism. Existing negative paths remain
because their regression consumers still depend on them. Backend state stays in
its one service. New unsafe code is unnecessary; traps retain synchronous spans.

Verification: full connections and launch suites, console ABI18 regressions, host
checks, scoped C/Rust format, workflow and offline pin checks. Add exact negative
controls for using freeze token1 on the second copy and sending parent-generation
bootstrap to the second child. Preserve every failed run and freeze source/tool
bytes. Check owner size against unchanged16KiB and exact stream counts[36,51,8].
Successful terminal order: child generations1,2,3 exit72; parent generation1 exit0;
backend generations1,2 exit17. Host sends three /next lines, three child bytes and
one final echo-status/exit line after the fourth prompt. No job control, pipelines,
persistent filesystem, package installation or independent release acceptance is
claimed. Existing ASCII fixture-output exception applies.

Document results and next step in STATE, NATIVE-SHELL-STARTUP and workflow inventory.
Use rustfmt1.98 edition2024 and existing Clang21.1.8 reviewed style for touched files.
