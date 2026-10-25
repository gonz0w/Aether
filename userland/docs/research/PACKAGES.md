# Provisional TTY package inventory

Reviewed 2026-09-05. Shell/utility providers remain provisional. Clang/musl
experiment pins and bounded native results are recorded separately in STATE.
The [initial command/provider matrix](BASE-PROGRAMS.md) now records evaluation order,
builtin/external distinctions and native prerequisites (UL-064). Toybox awk, stty
and tr are excluded from the first candidate selection pending separate provider
review. No utility package has been admitted by this research.

The user accepted Clang-first development and musl evaluation; the remaining
providers below are recommendations requiring UL-009/011 research and tests.

| Role | Candidate | Gate before adoption |
| --- | --- | --- |
| C compiler/linker | Clang/LLD | Pinned SDK, inspected ELF output, target runtime tests |
| libc | musl | UL-002/003 native interface decision and UL-006 evidence |
| System/recovery shell | dash | Script, process, FD and recovery tests; build/config/dependency review |
| Interactive shell | Zsh | Job control, editing/completion, controlled startup paths |
| Terminal support | ncurses/terminfo | Correct serial terminal description; package data/compiler separation |
| Basic utilities | Selected Toybox applets; GNU and BusyBox alternatives | Per-command behavior, portability, dependency and maintenance review |
| Modern utility alternative | uutils | Aether Rust std/platform port feasibility and command compatibility |
| Editor/pager | Open | Evaluate a small maintained editor and pager after terminal behavior works |
| Init and packaging | sys-init and pkg-mgr | Their own contracts and integration evidence |
| Login/authentication | Open | Credential/grant/entropy contracts; no stock Linux login assumption |

Initial command requirements: ls, cp, mv, rm, mkdir, cat, chmod, ln, printf, test,
env, grep, sed, awk, find, sort, head, tail, wc, stty and basic process inspection.
Map builtins versus external utilities explicitly. Add make, archive/extraction,
verification and patch tools according to actual pkg-mgr workflows; its current
fixture requires GNU-compatible make, despite the broader POSIX-oriented goal.
Coreutils alone is not the entire shell/text/build tool set.

Zsh supports configuring modules into the binary, allowing an initial build
without dynamic module loading. Retain needed line editing/completion, review
startup files and avoid a default third-party plugin framework.
[Upstream build instructions](https://raw.githubusercontent.com/zsh-users/zsh/master/INSTALL)

Dash is a focused system-shell candidate, but smaller size is not proof of
security. [Dash manual](https://manpages.debian.org/trixie/dash/dash.1.en.html)

Toybox documents partial portability beyond Linux; validate only the selected
commands. [Toybox FAQ](https://landley.net/toybox/faq.html)
GNU utilities and BusyBox remain comparison candidates, not rejected on age or
license. [GNU coreutils](https://www.gnu.org/software/coreutils/),
[BusyBox overview](https://www.busybox.net/about.html)
Uutils reports platform-dependent functionality; native Rust fixtures do not
establish a Rust standard-library target. [Uutils platforms](https://uutils.org/coreutils/docs/platforms.html)

For each selected release UL-011 records license, maintenance/security reporting,
transitive dependencies, source authenticity, patches, upstream tests, unsupported
features and update ownership. Keep network services and privileged multi-call
applets out of the initial profile unless a current requirement justifies them.
This inventory is not a complete POSIX conformance claim or security audit.


The [POSIX consumer inventory](../compatibility/README.md) now supplies the
initial runtime and shell acceptance checklist for provider comparison. Package
selection cannot close unsupported process/FD/VFS/TTY interfaces by itself.

## Minimal utilities checkpoint (UL-065)

Toybox 0.8.14 cat/wc/printf/test/true/false now have a pinned, unmodified
[Clang/musl Linux-reference build and tests](../../experiments/toybox-reference/README.md).
The result strengthens feasibility for those applets only. Native admission,
source authentication and final provider selection remain separate gates.

[Awk/tr/stty checkpoint](AWK-TR-STTY.md): three source-pinned awk host builds pass 33 consumer cases; final provider and native acceptance remain open.
