# Initial POSIX compatibility inventory

UL-031, 2026-09-05. Applies the pinned Distribution PX-01–04 profile; canonical
shared requirements remain in Aether-standards. This is a userland-owned inventory
and test plan, not a new shared standard or a POSIX certification claim.

The [machine-readable inventory](posix.json) enumerates 28 initial consumer
families. Each records native status, adaptation limits, required witnesses,
work IDs and evidence. It is not an exhaustive list of POSIX functions/options.
[Original source snapshot](sources.json) binds the UL-031 inputs and historical inventory;
subsequent bounded updates retain their own checkpoint evidence.
The kernel-work hold was subsequently lifted; UL-032 updates the allocation row
with bounded native-memory consumer evidence. No full tier is promoted.

Use POSIX.1-2024 / Issue 8 as the requirements reference. The official
[exec specification](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html)
distinguishes image replacement and descriptor inheritance from simple launch.
The Issue 8 [pipe](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html)
and [dup](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html)
pages include pipe2, dup3 and FD_CLOFORK; those are explicitly tracked, not silently
omitted because an older POSIX checklist lacked them. Direct page retrieval
returned 403 this turn; official indexed excerpts support this limited review.
Full clause/option review is required before implementation or conformance claims.

## Native status snapshot

“Deliberately adapted” means only the described fixture behavior is demonstrated;
it does not promote the whole POSIX interface to conforming. Unsupported means
native behavior is absent or not established; compiled libc symbols and Linux
reference execution do not change that status. Proposed is design only.

| ID | Interface family | Tier | Native status | Work |
| --- | --- | --- | --- | --- |
| PC-001 | C entry, argv/env, data/BSS, TLS | c | deliberately-adapted | UL-003, UL-006 |
| PC-002 | malloc/calloc/realloc/free | c | deliberately-adapted | UL-006, UL-015 |
| PC-003 | read | script | deliberately-adapted | UL-007, UL-043 |
| PC-004 | write | script | deliberately-adapted | UL-007, UL-043 |
| PC-005 | close | script | deliberately-adapted | UL-007, UL-043 |
| PC-006 | dup | script | deliberately-adapted | UL-007, UL-043 |
| PC-007 | dup2 | script | deliberately-adapted | UL-007, UL-043 |
| PC-008 | open/openat | script | deliberately-adapted | UL-007, UL-043 |
| PC-009 | fcntl and descriptor/status flags | script | unsupported | UL-007 |
| PC-010 | dup3 | script | unsupported | UL-007 |
| PC-011 | lseek and shared file offsets | script | deliberately-adapted | UL-007, UL-043 |
| PC-012 | pipe/pipe2 | script | unsupported | UL-007 |
| PC-013 | fork | script | unsupported | UL-007 |
| PC-014 | exec family | script | unsupported | UL-007 |
| PC-015 | posix_spawn family | script | unsupported | UL-007 |
| PC-016 | wait/waitpid | script | unsupported | UL-007 |
| PC-017 | _exit/exit | c | deliberately-adapted | UL-006, UL-007 |
| PC-018 | sigaction/signal masks/kill | script | unsupported | UL-007, UL-008 |
| PC-019 | cwd/chdir/getcwd | script | unsupported | UL-007 |
| PC-020 | stat/fstat and file metadata | script | unsupported | UL-007 |
| PC-021 | directory traversal and mutation | script | unsupported | UL-007, UL-011 |
| PC-022 | stdio and formatted output | script | deliberately-adapted | UL-007, UL-044 |
| PC-023 | shell grammar/expansion/builtins | script | unsupported | UL-007, UL-013 |
| PC-024 | sessions/process groups/foreground selection | tty | unsupported | UL-008 |
| PC-025 | termios/isatty/terminal access | tty | unsupported | UL-008 |
| PC-026 | locale/encoding/width | tty | unsupported | UL-009, UL-013 |
| PC-027 | identity and credential views | base | deliberately-adapted | UL-010 |
| PC-028 | utility provider set | base | proposed | UL-011, UL-012 |


The [bounded libc file witness](../../experiments/native-files/LIBC.md) adds
four-descriptor service-file I/O, read-only single-component open and bounded
public lseek. Its nineteen descriptor/file regressions preserve earlier evidence.
The [older stream contract](../NATIVE-DESCRIPTORS.md) remains a separate profile.
The [bounded buffered-file witness](../../experiments/native-files/STDIO.md)
adds a tested FILE subset and flush-error handling. Openat, formatted I/O,
permissions, blocking/signal semantics and descriptor inheritance remain
unsupported or unestablished. No tier is promoted based on
counting passing rows; every required case and prerequisite must pass.

## First shell acceptance cases

These are planned tests, not executed results. Pin the shell and utility builds
first, use a private scratch namespace, name all inherited descriptors/grants,
and record exact input bytes, stdout/stderr, status and cleanup. Start with C
locale, controlled PATH and no startup/plugin files. Add Unicode under an explicit
later locale profile rather than assuming a host default.

| Case | Workload and expected observation | Negative/control and cleanup oracle |
| --- | --- | --- |
| SH-01 commands | Quoted arguments, empty arguments and controlled environment reach a helper byte-for-byte | Deliberately altered argument must fail; no accidental expansion or host PATH fallback |
| SH-02 execution | Run a helper with a known nonzero exit; invoke a missing and a non-executable path | Distinguish command lookup/permission failure from runner absence; failed exec leaves shell able to run the next command |
| SH-03 redirection | Write/read a scratch file; append; redirect stdout and stderr separately and through duplicated descriptors | Denied target does not execute the external helper or truncate an unrelated file; check exact file bytes and open-handle inventory |
| SH-04 pipeline | Finite numbered writer through a reader that exits after its first record | Bound completion; distinguish EPIPE/default SIGPIPE/observed child status from a stalled writer; no surviving child or leaked ends |
| SH-05 pipe lifetime | Keep one duplicated writer open, then close all writers | Reader cannot report EOF before the last writer closes, and must terminate after closure |
| SH-06 inheritance | Helper reports allowed descriptors after fork and exec, including CLOEXEC/CLOFORK cases | A deliberately leaked descriptor fails; do not infer absence from descriptors 0–2 alone |
| SH-07 substitution | Command substitution produces a known byte sequence and status behavior, with quoted and unquoted contexts | Check trailing-newline/expansion semantics against the exact shell spec; bound child/reap cleanup |
| SH-08 cwd and scripts | cd into a scratch directory, run a script through the selected shell, execute lists/functions | Failed cd preserves prior cwd; paths stay in delegated namespace; executable-script/shebang policy is explicit |
| SH-09 interactive jobs | Foreground job, Ctrl-C, suspend/fg/bg and background terminal access in a PTY | Check process groups, terminal modes, prompt recovery and expected stop/continue outcomes; not just rendered text |
| SH-10 disconnect | Close the controlling session while a job and inherited pipe ends exist | Inventory children, descriptors and grants; report incomplete cleanup honestly rather than treating timeout as success |

SH-01–08 are the useful script-shell gate; SH-09–10 require native TTY/session
support. Exact helper protocols, signal expectations and shell-status oracles
belong in the future executable harness. Shell syntax/expansion cases follow the
[Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html).
The user's interactive choice remains Zsh; a smaller system shell remains a
candidate until these cases and its dependency/security review pass.

## Evidence promotion and remaining scope

A new result records source/patch/tool/artifact hashes, exact target profile,
commands, positive case, semantic control and cleanup evidence. Host-tested and
target-tested are evidence layers; deliberate adaptations remain labelled even
after target tests pass. Missing tools, skipped cases, watchdog expiry and unrelated
crashes cannot close a case. A matching libc symbol is not execution evidence.

Threads, networking, file locking, clocks/timers beyond selected references,
wide-character/locale completeness, regex/globbing libraries, permissions/links,
optional POSIX groups and full shell grammar need inventory expansion before a
broader claim. Initial manifest/provider decisions stay UL-011/012; authentication
stays UL-010. UL-013 retains detailed clause coverage and performance protocol:
fixed workloads and platform, startup/RSS measurement method, at least ten
repetitions for comparative reports, and explicit failure samples under PF-01–03.
No performance baseline or numerical product budget is created by this inventory.
