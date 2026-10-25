# Transactional exec preparation — 2026-09-10

This slice reviews the real loader/ownership boundary and implements pure candidate
state constructors. It does not install a native exec operation or run a replacement
image in QEMU. Previous164 connections and five launch results remain historical.

Execution.forImage prepares a validated entry/stack with fresh registers, x87/MXCSR,
FS/TLS metadata and empty wait/clear-TID registration, retaining the old signal mask.
Pending State.forImage retains queued occurrences, converts caught actions to default
and preserves ignored dispositions in canonical records without old-image pointers.
Neither constructor dereferences a user pointer, allocates, mutates its source or
publishes state. Image/pointer validation and old-context cleanup are future caller
obligations, not established by these constructors.

The [pre-code commit review](../../NATIVE-SHELL-STARTUP.md#transactional-exec-preparation--2026-09-10)
identifies why whole-State launch/copy cannot substitute for exec: generation/PID,
parentage, grants and lifecycle must remain while mappings and image state change.
It records required admission, alias/CR3 exclusion, descriptor/CLOEXEC coordination,
commit observability and rejection/lost-reply controls. A full extra State arena is
not yet selected. No trap number, owner service or cross-project ABI is introduced.
The connection owner still owns descriptor policy; native enforcement must not gain
ambient path, PID or executable authority.

The two new host tests cover source nonmutation and candidate independence, fresh
full frame/FP state, preserved mask/pending, reset caught handlers, canonical ignored
records and repeated construction. Queued signals whose new default ignores them
remain pending for ordinary delivery/discard policy. These are value-transition
checks, not evidence of failed-exec atomicity, native mapping cleanup, thread stop,
CLOEXEC, exactly-once commit or SDK/dash acceptance.

Final checks pass the aggregate Zig/Python suite (including98 Python tests), all39
direct execution/signal tests, scoped Zig formatting, standards, workflow and diff
checks. The direct host test executable is retained with its digest. Commands,
UTC times, host/tool identity and source/archive digests are recorded adjacent.
No target run was selected because the constructors have no native call sites;
fresh native process/memory/signal/command and SMP regressions are required when
replacement is wired into dispatch/mapping behavior.

Attempt1 preserves a test compile failure: the new test called consume instead of
the existing commit method. Neither failed Zig test binary ran. Attempt2 retains
the corrected aggregate/direct passing checks. Final checks repeat after the local
reference/workflow/STATE update. All attempt source archives are read back and
verified. Prior evidence, released pins, installed SDK and siblings are unchanged.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_execution.zig \
  --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Only native_execution.zig and native_pending.zig source implementations change;
there is no native_c dispatch or existing-profile behavior change in this slice.
The next step is bounded admission/commit and a publication gate, with explicit
retained image identity, old-image continuation on rejection, same-PID replacement,
FD preparation and native failure controls. R1 remains unfinished.
