# First Zsh consumer closure — UL-009

[Issue7](https://github.com/gonz0w/Aether/issues/7) owns this source/configuration
handoff. The release target remains an ISO booting through sys-init into serial
Zsh with persistent OpenZFS, a working runner and native package management.
This document selects the smallest useful Zsh consumer to expose its real missing
interfaces. Source authentication or a host build does not qualify an Aether
shell, terminal, executable loader or assembled ISO.

## Authenticated inputs and licensing

The machine-readable [manifest](zsh-consumer-v1.json) pins Zsh 5.9.2 and
ncurses 6.6 archives, SHA256s, detached signatures, upstream keys and actual signer
fingerprints. [Zsh's release directory](https://www.zsh.org/pub/),
[its published checksums](https://www.zsh.org/pub/SHA256SUM),
[ncurses's announcement](https://invisible-island.net/ncurses/announce.html) and
[signing-key publication](https://invisible-island.net/public/public.html) are the
primary provenance sources. Zsh's checksum matches its published list; ncurses's
checksum was computed after its detached signature passed. Signer association is
through official HTTPS publication, without independent web-of-trust assurance.

Verify both checksum and signature before extracting or running configure. Use
an isolated keyring and require the listed primary fingerprint; a valid signature
from another key is insufficient. Reject missing signatures, altered archives,
absolute/traversal paths, unexpected roots and excessive expanded input. The
retained local acquisition used at most 20000 members, 128MiB expanded total and
16MiB per member. Current source dependencies stay pristine and separate from
compact evidence; this repository does not redistribute archives or SDKs.

Preserve Zsh `LICENCE` and file-specific notices. Its core is permissively licensed;
some shipped shell functions carry GPL terms. The selected binary/function
installation omits the entire shipped function corpus. Preserve ncurses `COPYING`
and the selected terminfo entry's inherited notices. Recipes and Aether's BSD
license do not relicense upstream material. The manifest pins both license files
and the actual source files used for requirement discovery.

## Selected configuration

Use the manifest's exact configure arguments, with explicit target compiler,
headers, libraries and staging prefix. Build out of tree. Zsh core plus static
`zsh/zle`, `zsh/complete` and `zsh/compctl` supplies line editing and basic builtin
completion. `complete` depends on `zle`; `compctl` depends on both. Rich `compinit`
completion, optional networking, curses, PCRE, GDBM, capabilities, newuser and
dynamically loaded modules are excluded. Core builtins remain present; excluding
an optional module does not remove the core's process or libc requirements.

After configure and before the first build, edit **every** generated
`config.modules` row according to the manifest. Preserve the main pseudo-module
apart from clearing its functions field. Only the three selected optional modules
have `link=static auto=no load=yes`; all others have
`link=no auto=no load=no`. End each row with unquoted `functions=`. The field
extends to end of line, so `functions=''` is incorrect. `--disable-dynamic` alone
would make many optional modules static. If changing a compiled configuration,
run upstream `make prep` before rebuilding. Inspect final rows and linked objects.

Link only the selected static `libtinfo.a` from the pinned ncurses build. Its
`tgetent`/`tgetstr`/`tgoto`/`tputs` compatibility API supports ZLE without full
ncurses or the optional `zsh/terminfo` module. `--disable-termcap` removes runtime
text-termcap parsing, not this API. Explicit `--disable-widec` fixes the archive
name/configuration; UTF-8 ZLE depends on real libc wide-character/locale semantics.
Build only the terminfo archive, rather than installing unneeded libraries.

Zsh configure also probes full curses independently of `--with-term-lib`. Select
`zsh_cv_ignore_ncurses=yes` to omit that optional discovery, and pass the exact
current `libtinfo.a` path in `LIBS`. This disables an unused feature; it supplies
no successful syscall, header or function test. Keep actual termcap checks and
inspect the final link. The host reference without this selection pulled in the
system ncurses library and was rejected as the wrong dependency closure.

Retain compiled database support. Before native execution, select the actual
serial terminal frontend, matching `TERM`, one entry and its transitive `use=`
closure. A UART does not identify a terminal emulator. Build host `tic` from this
same release, preserve inherited entry notices and install only reviewed data in
an explicitly granted directory. Disable home lookup and sanitize terminfo and
termcap environment overrides. No frontend or entry has been native-qualified.

Launch one nonlogin `zsh -f -i` with controlled environment and granted cwd.
`-f` alone still permits a compiled global zshenv; `--enable-etcdir=no` and no
per-file overrides remove that path. No startup scripts, plugins or persistent
history file are selected. Do not introduce authentication/account provisioning
or grant authority from HOME, UID, path strings or terminfo lookup.

## Native requirements and observable acceptance

Source lines refer to the exact authenticated release archives. The manifest
carries the expanded matrix and inspected-file hashes.

| Feature | Source entry points | Required behavior and owner |
| --- | --- | --- |
| Startup/descriptors | Zsh `Src/init.c:628,1094,1327` | Actual terminal acquisition, isatty, fcntl/dup/close/CLOEXEC, allocation, errno, locale and truthful identity lookup; #6/#8. |
| ZLE editing | `Src/Zle/zle_main.c:240,589,848`; `Src/utils.c:1751` | Real termios transformation, readiness/read, EOF/EAGAIN/EINTR, deadlines, winsize and terminal restoration; #6/#8. |
| Terminal rendering | `Src/init.c:791`; ncurses `ncurses/tinfo/read_entry.c:588` | Selected compiled terminfo readable through granted FS authority, real output and honest padding/timing; #6/#9/#10. |
| Basic completion | `Src/Zle/compctl.c:2187,2195,2264` | cwd/path resolution, directory enumeration/stat/access, truthful denied/missing results without leaking foreign names; #9/#10/#12. |
| UTF-8 | `Src/Zle/zle_main.c:1014`; `zle_refresh.c:656`; `Src/zsh.h:3301` | Real locale, conversions/classification/width and fragmented input; #6/#8. Forced multibyte configuration does not prove libc support. |
| Commands/pipelines | `Src/exec.c:330,489,5127` | Actual fork/execve/pipes/wait and immutable authorized executable acquisition; #8/#12. Missing `/bin/sh` fallback remains a failure. |
| Foreground jobs | `Src/signals.c:111,285`; `Src/utils.c:4738` | Signals/masks, stopped/continued waits, process groups and foreground TTY authority; #6/#8. Disabling MONITOR cannot qualify job control. |

The first proposed native workload is one finite pre-admitted session with a
small granted directory: prompt and builtin output; ASCII cursor/backspace edits;
one filename TAB completion; fragmented UTF-8, combining and wide-character edits;
missing/denied filesystem reads; EOF/disconnect and terminal/resource restoration.
Add one pinned external helper only when actual #8/#12 interfaces exist. Require
exact expected output/status, no stale/foreign authority, unchanged denied state,
complete process/channel/handle settlement and no unknown outcome called clean.

Pipelines, substitution, redirection and genuine Ctrl-C/Ctrl-Z/jobs/bg/fg are
separate required acceptance tiers. A prompt alone does not close them. Measure
code/data/resident/stack/heap fit under the existing envelope before selecting
native artifacts or a transcript. Do not enlarge limits or provide successful
syscall/ioctl stubs to make Zsh start. Native budgets, frontend, exact grants and
artifacts require a concrete later selection; no guest is selected here.

## Reproduction and evidence limits

Follow root [retention and test cadence](../../docs/DEVELOPMENT.md). A host
reference build answers only whether the chosen module/static-library closure is
buildable. Use pinned Clang 21.1.8, isolated build directories, explicit include and
library paths, existing owned-process cleanup, one 300-second aggregate,
180-second leaves and 4MiB streams. Preserve failed attempts and source/tool
hashes; remove owned compiled outputs. Never treat Darwin system libraries,
Mach-O inspection or host terminal behavior as an Aether ELF/API result.

The configuration sequence is: ncurses configure with the manifest flags and
explicit prefix/database directories; `make -j2 sources`; from its `ncurses/`
build subdirectory, `make -j2 ../lib/libtinfo.a`. Configure Zsh with that build's
`include/` and `lib/` paths, apply the complete module selection, then `make -j2`.
Inspect final `config.h`, `config.modules`, complete link inputs and native binary
dependencies. A target build must use the actual pinned Aether musl/SDK and inspect
ELF/ABI and undefined APIs; no configure-cache forced-success values are selected.

Exact private receipts remain local. Public checks cannot reconstruct private
standards or SDK inputs; [availability](../../docs/PUBLIC-SOURCE.md) applies.
Separate handoff review and protected PR checks are required. Subsequent runtime
work stays in the linked issues rather than a second Markdown task queue.

## Bounded host observation —2026-10-25

The final isolated Darwin reference build and inspection passed in 68.698 seconds.
Only main/ZLE/complete/compctl were selected and loaded. `whence` confirmed the
zle/bindkey/compctl builtins; basic keymap/completion tables were inspected and
loading omitted `zsh/net/tcp` failed. The binary contains the termcap functions
from the exact local static archive; its dynamic dependencies are host libiconv
and libSystem. Global startup files and dynamic loading are disabled in final
configuration. The receipt retains 50 module-object names from `stamp-modobjs`
and the separate `Src/main.o` link input: 51 Zsh objects in this host build.
Sources stayed pristine and owned outputs/process groups were removed.

Earlier attempts remain retained locally: default wide-library naming selected
the wrong archive target; optional curses discovery introduced a system library;
and an inspection used a parameter supplied by an intentionally excluded module.
The last probe was corrected to use core `whence`, preserving the module closure.
No host terminal session, UTF-8 behavior, target ELF, Aether syscall support,
native resource fit or ISO boot was qualified. Upstream archive/signature checks,
source/configuration review and scoped inventory checks passed; the complete
public inventory still depends on omitted historical/private inputs.

The subsequent [Aether target-link status](ZSH-TARGET-LINK.md) records the public
outcome and remaining admission/runtime boundaries. Its exact SDK and artifact
qualification evidence stays local; the linked GitHub issue owns continuation.

The owner-approved [bounded application profile](../../docs/NATIVE-ZSH-APPLICATION.md)
defines a separate host-only admission profile under issue69. Its trial resource
allowance is not native Zsh, TTY or heap/stack qualification.
