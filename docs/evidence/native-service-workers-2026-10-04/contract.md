# Owner-local live workers (before code)

Requirement: exercise the retained host workload's 82-worker/20.5 MiB requested
stack lower bound in the existing private 32 MiB native service owner. This trial
is not a measured native engine peak or adequate full-engine memory budget.
`native-service-workers` requires service memory plus thread pair/origin/reuse;
keep 512 monotonic lifetime admissions, exact IDs and unchanged capabilities.
Only domain 0 receives 82 live records; three companions retain two each. No
public quota/configuration API, CPU identity, provider or TCB/SDK adoption change.

Keep child records off-stack in separate static owner arrays. State holds a
bounded child view only in this profile; derive views from authoritative domain
identity on boot/reset and clear only the selected owner's records. Context
pointer lists stay temporary and bounded (at most 83 pointers plus count), with
actual owner length; they must not escape a synchronous IF-clear call. Default
embedded child arrays and actual context set/order remain. Stop/clear-TID and
wait cleanup precede reset, mapping zero/reuse or retirement. No global mutable
registry, cross-owner child alias, scheduler policy or implicit authority.

Test 82 simultaneously live 256 KiB bare stacks plus 4 KiB FS cookies, all held
through atomic readiness/release. Small peer fills two 4 KiB stack/TLS slots and
rejects a third. Full-slot rejection must not spend the next ordinal; exact-ID
retirement while running rejects, stack/TLS pins hold, all clear-TIDs/terminal
status verify, retirement/unmap restore quota and a fresh domain generation gets
fresh records/grants. Test stop with the whole set live and generation replacement.
An actual omitted reset rebind must fail the named worker admission witness;
release builds reject it, prerequisites reject exactly. Bare cookies are not a
production musl TCB or a native upstream taskq/engine execution claim.

Run full host/pins/workflow, full older default/large pair and pthread lifecycle
matrices because context list adapters are touched, current memory matrices,
selected origin/reuse/entropy and seven M4. Fresh main and stop/control witnesses
bind SDK/tool/header/source/command/time/ELF/ISO bytes; 30-second VM watchdog and
3-second owned teardown unchanged. Retain failures and archive readback before
owned duplicate cleanup. Independent reader/SDK, stack high-water, syscall latency,
full-engine startup/fini/restart, persistent filesystem and R1 remain open.

Simplicity/security: raising every domain array wastes memory and obscures the
selected owner's quota. Static 82+3*2 pools and derived bounded views preserve
existing State ownership without a heap or general thread allocator. A temporary
pointer list composes existing wait/wake helpers; it adds at most about 672 bytes
on the existing 64 KiB exception stack, no persistent pointer cache. New unsafe
lifetime: view reconstruction after whole-State reset and temporary context-list
borrowing. Bind/clear only checked owner arrays; no caller address conveys a view.

Large-profile stack/TLS permission preflight also uses the existing validated
range cursor to visit each backing record once; immutable/anonymous and whole
range checks still precede publication. Default typed slot-order checks stay.
This prevents 82 large-stack admissions from repeating quadratic slot lookups.

First capacity passes, but the stop fixture compiled its helper only once without
per-case STOP_WORKERS. The service exits normally, and the stop supervisor rejects
that exact unexpected outcome (401). Preserve all bytes. Compile the helper with
each case's flags; also check each generation's first storage ID (3/4) explicitly.
No runtime changes are needed, and all final cases run fresh.
