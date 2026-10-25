# Aether Zsh target-link status

[Issue65](https://github.com/gonz0w/Aether/issues/65) owns this bounded experiment
and its continuation. The [source/configuration handoff](ZSH-CONSUMER.md) and
[manifest](zsh-consumer-v1.json) define the required Zsh and terminal-library
closure. Exact SDK associations, artifact measurements, provider inventories,
commands and raw receipts remain local.

The selected closure compiles and links with actual Aether providers. The
unchanged ordinary-process parser rejects the candidate's resource footprint.
A separately selected size-only comparison preserves required modules, ABI and
protections but does not clear admission. This is a capacity blocker, not an
accepted native shell or bootable ISO.

## Admission boundary

The public [ELF contract](../../kernel/native_elf.zig) and
[launch model](../../kernel/native_launch.zig) retain their existing ordinary
process limits: a 1MiB file and 128 backing pages including 16 main-stack pages.
Those limits, the parser, SDK providers and historical seals were not changed to
obtain a successful result. Further footprint work or a distinct application
profile needs its own bounded contract and review. No such change is selected
by this report.

The experiment uses an explicit Zsh entry and input inventory. Dash objects and
the old Dash-specific application entry are not relabeled as Zsh. Upstream
sources remain pristine. Target compilation uses actual target headers and
libraries; necessary authenticated host generators use isolated host inputs.
No target configure/test execution or API-success implementation is used.

The comparison changes only source compilation for size and section garbage
collection. Required modules, startup/TLS, stack protection, frame/fork and
FP/SIMD assumptions remain part of the experiment. No LTO or feature-removal
variant is claimed.

## Qualification limits

Source pin, contamination, module, target-execution and provider checks have
local evidence. Some actual-image mutation controls remain unavailable while
the positive candidate fails admission. A generic parser rejection cannot
substitute for each semantic denial. Failed attempts remain retained; owned
processes and generated outputs were removed. The target bytes are historical,
not a retained runnable deliverable. [Public input availability](../../docs/PUBLIC-SOURCE.md)
applies; private SDKs and qualification details are not included here.

Native behavior still requires real TTY/descriptor/mode semantics under #6/#8,
filesystem terminfo/completion under #10/#11 and executable acquisition under
#12. Audit libc internal stdio and exit routing explicitly: an external `open`
binding does not prove `fopen` uses it, and an `_exit` wrapper does not establish
all `exit`/`_Exit` cleanup paths. Symbol presence is not native support.

No guest, IRQ timing, heap/stack peak, actual ZLE/job-control or assembled ISO
qualification follows from this link experiment. Exact local measurements and
review records remain available to the owner for the next decision.
