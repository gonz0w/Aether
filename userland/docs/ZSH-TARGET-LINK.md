# Aether Zsh target-link status

[Issue131](https://github.com/gonz0w/Aether/issues/131) selects the current offline
build of actual pinned Zsh with the current SDK and terminal providers, following
[issue130](https://github.com/gonz0w/Aether/issues/130)'s reviewed recommendation.
The outcome is a real executable, provider-route inspection and structural fit;
no kernel image or guest is selected by this work.

## Current external entry

The selected [entry](../experiments/filesystem-service/fd-zsh-external.c) owns one
stable off-stack descriptor startup object. It calls the real native startup API
once, checks the admitted identity and role, and publishes that same object to
the existing descriptor bindings. An initialized thread-local guard records the
entry's once-only transition and supplies real TLS consumed by the program.
Scalar calls and the scoped stdio vector adapter use that context. Readiness
reports admission, not a visible Zsh prompt.
The entry sets the approved canonical mode with SIGINT ignored before calling
actual Zsh; later handler installation remains Zsh's responsibility.

Canonical bindings imply SIGNAL, MODE, duplex and EXTERNAL startup. Historical
fork/exec/dup2 providers and their entries cannot be combined with this selection;
the existing guards remain. Unsupported operations must return truthful errors.
The current build excludes the mktemp entry and standalone C terminal probe.
For this selected entry, compile only `fd-zsh-external.c` and
`fd-libc-bindings.c` with `-D__real__exit=__real__Exit`, and link with
`--wrap=main --wrap=_exit --wrap=_Exit`. The new `_Exit` wrapper delegates to the
existing descriptor finalizer. Its raw termination call resolves real SDK
`_Exit`, avoiding recursion through SDK `_exit` back into the wrapper. Libc
`exit` retains its own fini/stdio work before reaching that finalizer. These
flags do not change older application builds or the shared provider source.

The build preserves the [required source/module closure](ZSH-CONSUMER.md), current target
headers/CRT/libc, memory provider and scoped stdio adaptation. Host generators
remain isolated; no target configure execution or SDK rebuild is selected.

Inspect each new executable's actual libc-internal stdio, fcntl, memory and
termination routes. A resolved public symbol does not establish its internal
callers. Missing provider wiring can be corrected here; a required semantic
change beyond existing providers becomes a concrete bounded follow-up, without
success stubs or a guest that relies on unresolved routes.

The approved [large application parser](../../docs/NATIVE-ZSH-APPLICATION.md)
allows 384 total image-plus-stack pages, including the existing 16 stack pages,
and 640 total backing pages. Its structural acceptance does not measure Zsh's
runtime heap, recursive parser or signal-handler demand. Ordinary profile
rejection remains required. The kernel's large-application-plus-MODE exclusion
stays intact; separate approvals do not authorize deleting that guard.

Matching Owner startup/namespace, real terminfo file access, locale/identity/cwd,
readiness and actual stack/heap/signal/stdio/exit behavior remain runtime gates.
A later labelled builtin-only `zsh -f -i +m` observation would not qualify
foreground groups, external commands, persistence, packages or R1. The product
still requires sys-init into actual interactive serial Zsh and persistent OpenZFS.
Exact build commands, input identities, failed attempts and results remain in
compact local evidence; public replay requires the private prerequisites.

## Current offline result

The current Zsh/tinfo closure compiles and links with the selected current
providers. The actual 1,268,656-byte executable passes the current application
parser, loader layout and backing checks at 312 pages including the 16 stack
pages. The ordinary profile rejects it. Its four-byte initialized TLS guard is
inside a writable load segment and fits the existing TLS route. Remaining
backing capacity does not establish runtime heap or stack sufficiency.

Scalar terminal input/status/modes and scoped buffered output reach the admitted
context. Actual linked readback confirms that normal libc `exit` finishes its
fini/stdio work, reaches the existing descriptor finalizer once, and terminates
through real SDK `_Exit` without a wrapper cycle. Filesystem-backed terminfo
remains blocked: ncurses reaches libc's
internal `fopen` and buffered-read routes, which do not yet use admitted file
Sources. The ordinary Owner's namespace/startup path also needs matching Zsh
integration. These are concrete runtime work, not errors to hide with successful
stubs. No kernel image, guest or interactive Zsh qualification follows from this
build; the combined-profile guard remains in place.

## Focused checks and reproduction

The [entry harness](../experiments/filesystem-service/fd-zsh-external-tests.c)
links the actual entry, startup and descriptor core. Its nine host cases cover
single initialization, identity/role refusal, startup/bootstrap/readiness errors,
cleanup, FD10 scalar/vector I/O, partial source counts, errno, finished-state
rejection and the `_Exit` delegation. A compiling omission of that delegation
must fail the same cleanup assertion. Auxv, raw kernel calls and signal installation are host doubles;
these tests do not run Zsh. A strict SDK target compile and named incompatible
flag rejections check the selected target boundary.

The private development workspace supplies the frozen `entry-checks.py` recipe
and `tools/zsh-target-fit.py` coordinator recorded in issue131. The latter builds
actual Zsh/tinfo and runs current parser/layout/backing checks. Each uses the
existing owned-process helper, a 300-second aggregate, 180-second child limits
and bounded output. Public source alone cannot replay those private-input
commands. Keep their compact results and failures; remove owned generated
binaries/maps/configuration after review and checkpoint under root retention.

## Historical ordinary-profile link

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

The subsequent owner-approved resource decision is implemented under
[issue69](https://github.com/gonz0w/Aether/issues/69) and the distinct
[application contract](../../docs/NATIVE-ZSH-APPLICATION.md). The ordinary-parser
rejection above remains the historical result; the subsequent fresh selected-profile parser and configured-kernel checks pass
in their focused host scope. Issue69 and issue70 hold the current complete-host
and integration disposition; native qualification remains separate.
