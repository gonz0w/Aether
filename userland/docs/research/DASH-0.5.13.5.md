# Dash 0.5.13.5 consumer audit

UL-034, 2026-09-05. Source revision is the archive in
[the source lock](../../experiments/dash-reference/source.lock.json), not a moving
branch. [Build and twelve reference outcomes](../../experiments/dash-reference/README.md)
are complete within their stated Linux-emulation scope. Dash remains the
system/recovery-shell candidate, with Zsh the interactive destination.

## What the actual source requires

Paths/line numbers below refer to the pinned upstream archive. The retained
libc-imports.json subtracts definitions across dash's own objects, leaving 99
external symbols; many are pure libc helpers. Import presence is distinct from
execution and from the underlying musl syscall requirements.

| Source path | Consumer behavior | Native consequence / work |
| --- | --- | --- |
| src/jobs.c:974–1016; src/eval.c:505,592,651,916 | fork for subshells/pipelines/substitution; vforkexec for eligible external commands | A fixed-image factory cannot replace copied shell state. Audit both musl paths, parent suspension, child error/exit and grant inheritance before selecting an adaptation. UL-003/007/015/035 |
| src/exec.c:153–171 | execve; ENOEXEC retries /bin/sh | Executable/path authority, argv/env replacement, CLOEXEC, failed-exec state and an explicit shell path are required. ENOEXEC fallback is still untested. UL-007/035 |
| src/jobs.c:1151–1215 | wait3 in this config; WNOHANG, signal interruption and job bookkeeping | Translate real child statuses, reaping, SIGCHLD/masking and interruption; startup instance IDs are insufficient. UL-007/035 |
| src/input.c; src/redir.c:470–481 | F_DUPFD_CLOEXEC saves internal FDs at >=10; dup2 and restoration | Current eight-slot facade cannot even host ordinary script input at FD 10. Need bounded but sufficiently large tables, separate descriptor flags and shared open-file state. UL-007/035 |
| src/redir.c:206–268; src/cd.c; src/expand.c | open/stat/access, cwd and directory enumeration | Delegated path namespace, modes, shared offsets, umask and honest denial. Glob and tilde expansion also reach directory/passwd lookup. UL-007/010 |
| src/eval.c:566–651; src/redir.c:331–401 | pipes, substitution and here-documents; long here-docs use a forked writer when memfd is disabled | Closing the last endpoint drives EOF/EPIPE; bounded buffering must block/wake correctly. Disabling Linux optimizations does not remove fork/pipe needs. UL-007/035 |
| src/trap.c; src/jobs.c; imported sigaction/sigprocmask/sigsuspend | Signal table, handlers, masks, child notification, wait races | Signal transport/frame/restore semantics need an explicit musl audit and native owner agreement. A successful stub is unacceptable. UL-003/007/015 |
| src/jobs.c; src/histedit.c | get/setpgrp, tcgetattr, tcgetpgrp, tcsetpgrp, terminal access | Compiled job control remains; twelve script tests do not establish a TTY. UL-008/009 |
| src/main.c; src/var.c; src/miscbltin.c | UID/GID views, getpwnam, limits, time and environment | Developer fixed identity cannot become production root authorization. Account lookup and limit policy remain separate. UL-010 |

The current kernel native memory/loader profile permits 128 total backing pages
including a 64 KiB stack. The reference ELF's segment sizes alone do not prove it
will fit during parsing, fork, or large scripts. It also still contains Linux
syscalls and is not an admissible native transport artifact. Size/resource
measurement belongs to UL-013 and a future native shell workload.

## Configuration and dependency decision

Use upstream `--without-libedit --disable-tee --disable-memfd-create` for this
reference candidate. Keep LINENO and default internal matching. The selected
static target dependency closure is dash plus musl, with LLVM/LLD and generated
build helpers as tools. There is no ncurses, libedit or GCC runtime dependency in
this artifact. This is a concrete feasibility result, not a security ranking.

Upstream COPYING carries BSD-style terms and a separate GPL-2.0-or-later notice
for mksignames.c; it explicitly notes that the generator's output is linked into
dash. Preserve the complete upstream notices and review generated-output and
combined binary distribution obligations under UL-016. Do not relicense upstream
content under this repository's first-party BSD-2-Clause default or reduce the
third-party inventory to a single package label. Musl's own notices remain required.
No binary redistribution or final license clearance occurs in this experiment.

## Next bounded work

UL-035 completed the [musl audit and nine-case witness](MUSL-PROCESS-FD.md).
Its original bounded scope was to audit the exact paths and construct a
small reference process/descriptor witness that can later run against an agreed
native implementation. Cover copied memory versus shared file offsets, CLOEXEC,
failed exec preserving caller state, child status/reap, early-reader EPIPE and
failure cleanup. Retain signal and here-document gaps explicitly. Use those
results to support owner-reviewed requirements in Aether-standards before native
implementation; do not infer authority to add kernel/process services here.

Primary source: [upstream dash](http://gondor.apana.org.au/~herbert/dash/), pinned
archive contents inspected locally. [Homebrew's packaging formula](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/d/dash-shell.rb)
provided the matching archive digest; its dated bytes are retained with evidence.
Moving links are research locators only. Source authenticity, security-fix review
and release eligibility remain UL-016.
