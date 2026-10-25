# Serial repeated command substitution

Requirement: drive actual interactive dash through the existing scoped UART
backend, with two substitutions entered at separate prompts in one shell, followed
by a fresh shell. Use AENMX003/ABI18, pinned native dash input/main/jobs objects,
existing pipe/fork/wait3 adapter and two-session console backend unchanged.

Session1 host input: `a=$(echo pipe); echo "$a"\n`, then after returned prompt
`b=$(echo pipe); echo "$b"\n`, then after returned prompt `exit 0\n`.
Session2: `echo clean; exit 0\n`. Each initial/returned prompt is observed before
sending its command; delay initial input briefly to require real EAGAIN progress.
Require two SHELL READY markers, four prompts, pipe output twice and clean once.
Owner independently verifies every stdin/stdout/stderr byte and cumulative offset;
pipe data itself must remain private and reach EOF before wait collection. Empty
UART reads retain the unapplied request without advancing positions or replying
EOF. Keep the console grant solely in the backend; parent direct access is denied.

Parent1 survives pipe/child/freeze generations1→2; parent2 creates no pipe/child.
The shared console backend resets stream state between sessions and stays alive
until both parents finish. Its replacement must lack the old UART grant. Two
parents, two children, actual backend and denied-grant replacement give six real
reclaims. Do not add dummy processes, quota, kernel, ABI, SDK or sibling changes.

Forbidden: prompt before completed child collection, child bytes leaking directly
to UART, fake EOF on EAGAIN, stale pipe/copy state, parent UART authority, backend
close before its second session, altered input/output accepted, false lifecycle.
Controls: host supplies a changed first command (owner2182 before fork/reclaim),
and old freeze token1 on second copy (owner2179 after exactly one reclaim).
Require ordered terminal/owner records and fail on timeouts or unrelated panics.
Unexpected faults/lost replies remain fail-closed fixture failures, not general
recovery. Live-pipe exec and combining this with the serial exec profile remain open.

Aether owns this producer; userland owns SDK and independent acceptance. Apply
O-02–05, I-01/03–06, E-01–08, local Coding/Testing and SE-01–05. Existing ASCII test
markers, dash `$ ` prompt and stdout/stderr roles stay unchanged under the scoped
Experience migration exception. No decorative output, capability disclosure or
released standards change. Read fixed-output rules; run experience/pin checks.

Simpler alternative: retain the tested `-c` workload. It cannot prove interactive
stdin resumption or UART lifetime. Reuse the current owner and console backend;
a focused serial driver avoids adding further mode flags to the existing exec
serial driver. It borrows that driver's bounded QEMU lifetime/log-retention pattern.
No new runtime service, allocator, unsafe block or wire format; fixed native-call
buffers are synchronously borrowed as before. Nothing old is removable yet: exec,
nonserial pipe and fault controls still cover separate required behavior.

Select focused positive/wrong-input/stale-token preflight before full274-case
connections, five launch and two console regressions; host/harness/format/workflow,
three offline pins and simplicity verification. Update native references, workflow,
Experience scope, STATE/ROADMAP and companion boundary. Freeze sources for qualified
runs, retain failed attempts and verify archives before deleting unpacked duplicates.
Independent reader/consumer acceptance and assembled R1 remain open.
