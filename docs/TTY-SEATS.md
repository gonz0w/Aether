# TTY terminal sessions and seats

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the TTY/package review. Implementation remains queued/partial under
[UP-07](../.planning/ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries).
[STATE](../.planning/STATE.md) records progress. A native Rust user-space TTY
service and ncurses/terminfo evaluation are the first direction; libtsm is the
leading later local-emulation candidate, not an adopted or qualified native package.
Exact protocols, production placement, package versions and wider features remain
scoped implementation work.

## Decision and responsibility

Separate device transport, TTY behavior, terminal emulation and graphical seat
policy. The kernel provides protected hardware access, IPC, execution/wakeup and
authorized signal mechanisms. A native Rust terminal service owns line discipline,
mode state and buffered I/O. Musl adapts supported POSIX calls to typed operations.
Applications receive authorized terminal references rather than device-wide access.

| Layer | Direction and responsibility |
| --- | --- |
| Serial/device transport | Grant-scoped hardware/stream owner with bounded input/output, interrupt and failure contracts |
| Native TTY | Rust user-space owner of line discipline, terminal modes, queues, readiness, dimensions and hangup |
| Process/session relationships | Authoritative process/session owner coordinating groups, controlling terminal and foreground selection with the TTY owner |
| Application terminal support | Evaluate ncurses/terminfo through the Aether musl backend for shell and text-application interfaces |
| Local terminal emulation | Evaluate libtsm screen/escape-sequence state behind an Aether display frontend when a local console is needed |
| Graphical seat policy | Capability-scoped user-space authority for active-session input/display delegation and handoff, later |

Aether owns enforcing mechanisms and native fixtures; Aether-userland owns its
assigned musl/runtime and package/end-to-end consumer work. General TTY/session/seat
production service placement and project implementation ownership require explicit
affected-owner agreement. Accepting Rust user-space service direction does not
silently expand the existing bounded runtime assignment. Sys-init retains startup,
supervision and session-admission/recovery policy within agreed contracts; pkg-mgr
retains artifact/install policy. Responsibilities may share a reviewed process;
there is no requirement for one service process per terminal or open descriptor.

## Serial TTY and bounded line discipline

Begin with the actual R1 serial-console and shell consumer. Publish the supported
canonical/raw mode set, input/output translations, special characters, echo policy,
line and queue bounds, overflow/backpressure and exact read/write completion rules.
Keep raw transport bytes distinct from human diagnostic fields and preserve stdout,
stderr and control identity until explicit redirection/merge. Distinct FD roles may
refer to the same physical terminal; they do not require separate UART hardware.

Canonical input supplies complete lines with supported erase/kill editing and echo.
An EOF control character such as Ctrl-D can end the current read without destroying
the device: buffered input and an empty-line EOF case have different results. Empty
open input, a zero-length request, temporary nonblocking unavailability and actual
disconnect remain distinct. Unsupported job-control behavior cannot be presented
as successful Ctrl-C/Z handling. A local cancellation fixture remains labelled as
that fixture until actual foreground signal semantics exist.

Raw input preserves the declared byte behavior. VMIN/VTIME, input translations,
O_NONBLOCK and signal interruption need explicit interaction rules for each enabled
profile; do not infer them from one-byte polling. Timed reads depend on the relevant
[calibrated clock/deadline slice](CLOCKS-TIMERS.md), not unqualified interrupt counts.
Define readiness from the supported read-completion semantics, including canonical
line availability, enabled timed/raw behavior, EOF/errors and buffered data.

[Service I/O](SERVICE-IO.md), [descriptor ownership](FILE-DESCRIPTORS.md) and
[native waiting](READINESS-WAITS.md) govern short counts, retained references,
backpressure, atomic observation/park, interruption and unknown completion. Accepted
output bytes, UART transmission, rendering and persistent storage are distinct.
Lost replies cannot justify duplicate output or fabricated success. Input is not
silently overwritten on exhaustion; choose a bounded documented overflow response.
Close of one duplicate reference does not hang up a terminal still held elsewhere.

## Typed terminal controls and state restoration

Musl implements the enabled isatty, tcgetattr/tcsetattr, drain/flush, window-size
and terminal-control interfaces through the actual resource owner. Native requests
have bounded schemas and explicit access rights; ioctl adaptation does not tunnel
caller pointers or arbitrary Linux control encodings. A stream or numeric FD is
not proof of terminal type or permission to change its modes.

Separate input consumption, output production, mode control, foreground selection
and recovery takeover authority. Validate supported values and caller/terminal
identity before effects. Unknown modes/commands fail honestly, preserving state
under the declared native contract; no successful no-op stands in for termios.
Mode changes coordinate against the current state/revision and declare immediate,
output-drain and input-flush effects for supported tcsetattr forms. Flush discards
data only through an explicit authorized operation, not an incidental reset.

Capture mode snapshots with terminal identity, owner generation and relevant
revision before temporary changes. Restore only a still-valid snapshot; an old
client cannot overwrite a successor's modes. Qualify normal exit, handled signals,
failed mode requests and stale restoration. Uncatchable termination requires an
authorized recovery/reset path, not a promise that the dead client restores itself.
GNU stty -g excludes window size, so its saved string alone is not a complete
terminal-state snapshot or a generation-protected restore capability.

Disconnect/owner death specifies pending input/output disposition, waiter results,
signal effects where enabled and reference cleanup before reuse. Do not replay
queued pre-crash input into a replacement shell. Recovery takeover is explicit,
generation-bound and supervised through existing policy. Retain the bounded kernel
emergency diagnostic path and its exact markers; it is not an application console
or a substitute for recovering ordinary service state.

## Sessions controlling terminals and job control

Keep process groups, session membership and controlling-terminal relationships at
their authoritative owners, with one owner per mutable resource. TTY foreground
selection refers to authenticated membership and current process/group generations.
Numeric PIDs, group IDs, /dev/tty paths or advisory UID zero cannot grant control.
Supported /dev/tty resolution uses the caller's authorized controlling-terminal
relationship rather than global discovery of another session's terminal.

When enabled, Ctrl-C generates SIGINT and Ctrl-Z generates SIGTSTP for the authorized
foreground group under the [signal contract](SIGNALS.md). Process groups and actual
stop/continue transitions must exist first. setsid/setpgid and tcgetpgrp/tcsetpgrp
adaptation must agree with the process/session owner; changing a libc field cannot
implement them. Background reads/writes and SIGTTIN/SIGTTOU behavior require the
supported policy, including applicable mode flags and exceptions, before job control
is advertised. Define foreground ownership after exit, disconnect and group reuse.

Fork/exec inherit only the controlling-terminal relationships and references allowed
by their enabled contracts; they cannot manufacture terminal/session authority.
Terminal modes belong to the terminal resource, not a writable per-process cache.
Qualify Zsh editing/completion, Ctrl-C/Z, fg/bg and restoration as a separate consumer
tier after the selected dash/system-shell path. A prompt or builtin-only interaction
does not establish working POSIX sessions, full job control or authenticated login.

## PTYs and terminal emulation

PTYs reuse the same TTY behavior with a master/slave transport. The terminal frontend
holds the master reference; the shell/applications use slave references through musl.
Define bounded pair creation, access/delegation, buffer ordering, resize notifications,
hangup, duplicate/reference lifetime and cleanup. Master/slave closure differs from
closing one FD alias. Pty names are namespace selectors, not authority; do not expose
an ambient global devpts view merely to satisfy an imported program.

PTY support provides a foundation for graphical terminals, terminal multiplexers
and later remote sessions. Those consumers still need their own process, transport,
authentication and lifecycle contracts; a pair of byte streams is not a qualified
PTY implementation. General PTYs are not required just to transport the R1 serial
shell, but they are a dependency for the later native local-terminal frontend.

On the serial baseline, the external terminal handles escape-sequence rendering.
Aether does not need a screen emulator to pass bytes to it. When Aether renders its
own local terminal, put emulator state in the frontend and keep rendering behind
the display contract. libtsm supplies terminal state; it does not supply our TTY,
PTY transport, renderer, font/layout engine, session or seat authority.

## Package evaluation and terminal descriptions

Retain [userland's ncurses/terminfo candidate](../userland/docs/research/PACKAGES.md)
and its [UL-008/UL-009 contracts](../userland/.planning/BACKLOG.md).
Evaluate ncurses' low-level terminfo/libtinfo subset first and add required curses
interfaces for actual consumers. Build against the Aether musl port; compile reviewed
terminfo entries with host tooling initially and package the necessary target data.
TERM describes the actual terminal/emulator and supported capabilities; serial
transport alone does not justify linux or xterm-256color. Provide conservative
unknown/TERM=dumb behavior. Do not use terminal labels as device authority.

Review exact source/version/license/digest, configuration, patches, dependencies,
locale/width behavior, filesystem access and upstream/native tests before package
admission. Wide-character ncurses configuration is a candidate, not proof of Unicode
editing. Separate compiler/tools from target runtime/data; no release/version or
package pin is selected here. The architecture is accepted; native package adoption
and independent consumer qualification remain open.

Keep [GNU stty first with BusyBox comparison](../userland/docs/research/AWK-TR-STTY.md).
The utility exercises terminal controls and cannot implement the underlying service.
Existing host/emulator or restoration evidence remains bounded, not native TTY
acceptance. Neither an installed utility nor musl alone supplies session semantics.

For a future local emulator, evaluate
[libtsm](https://github.com/kmscon/libtsm) first: upstream separates terminal state
from rendering/window management and describes an ISO-C-library runtime requirement.
Its fit still requires a pinned source/closure/license review, musl build, Rust FFI
ownership checks, bounded screen/scrollback/resize and malformed-sequence witnesses.
The Rust [vte parser](https://github.com/alacritty/vte) remains an alternative when
its parsing-only boundary is useful; additional screen semantics would be our work.
No complete kmscon or GPU terminal package is adopted by this choice of library.

The accepted [device-service and scoped /dev direction](DEVICE-SERVICES.md), under
[UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev), supplies
authorized terminal/device bindings and provider-generation lifetime. /dev/tty
resolves this caller relationship; an optional /dev/console resolves a delegated
normal console without exposing emergency diagnostics. Namespace publication and
FD closure cannot substitute for effective device/mapping/command cleanup.

## Graphical seats and device handoff

A graphical seat groups input and display resources assigned to an active session.
Keep this policy distinct from serial TTY line discipline and sys-init supervision.
Use delegated device/input/display authority with explicit activation/deactivation,
generation and recovery outcomes. Closing an application view or terminal emulator
does not implicitly stop unrelated services or transfer a physical seat.

An inactive session must lose effective access at the relevant device/route owner;
an advisory pause notification or FD close alone does not establish revocation of
existing mappings, queued commands or input delivery. Handoff qualifies stale input,
in-flight output, CPU mapping and device-specific DMA/command quiescence where
applicable before exclusive access is reassigned. Do not enable switching under
an unqualified revocation contract. The terminal frontend need not receive device-
wide MMIO/DMA access simply to display text through the display service.

[Libseat](https://github.com/kennylevinsen/seatd) can be evaluated as a compatibility
frontend when an imported graphical consumer needs its API. Existing seatd platform
backends are not a native Aether authority implementation. Any Aether backend maps
to actual capabilities/device owners rather than UID/root shortcuts or fabricated
Linux VT/DRM behavior. Multiple seats, global VT switching, Xorg/Mesa integration,
remote login and broad recovery remain later consumer-driven work.

## Experience simplicity and implementation sequence

Follow the pinned [TTY experience](vendor/aether-distribution/v0.1.0/TTY.md) and
[Experience adoption](EXPERIENCE.md): plain/ASCII and NO_COLOR paths, keyboard access,
40/80-column and narrow layouts, declared UTF-8/width behavior and preserved machine
streams. Qualify invalid UTF-8, combining/wide characters and control/paste handling
before claiming those modes. Bracketed paste, where supported, is editable input,
not automatic multiline execution. No default shell startup plugin/network fetching.

The simpler alternative is the existing serial byte stream with the external host
terminal. Keep it for transport and bounded fixtures. Actual shell mode changes,
foreground control and restoration need native authoritative TTY/session state;
ncurses, stty or a screen emulator cannot supply that OS boundary. A bounded Rust
service and typed controls avoid importing a large kernel TTY stack. Reuse ncurses
and later libtsm for their distinct application/emulation responsibilities. Their
total cost includes adapter/FFI, data packaging, state bounds, ownership and recovery.
No code is removed now; qualified replacement can retire fixture-only polling or
mode stubs after identifying consumers and migration obligations.

[UP-07](../.planning/ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries)
coordinates UP-01 references, UP-03 I/O/control, UP-04 readiness, UP-02 process/signals,
UP-06 identity/namespace and SI-01 timed reads. Preserve current backing/storage
priorities. Sequence native serial TTY, required ncurses/terminfo consumers,
session/job control, PTYs, libtsm local-console evaluation, then graphical seat
compatibility. R1-01/R1-02/R1-06 select the required terminal/boot slices; general
PTYs, graphics, seats and full future Zsh features are not blanket R1 prerequisites.

Exact ABI/mode layouts, service placement, limits and restoration/recovery protocols
remain scoped work. Require native owner and independent userland positive/denial
witnesses for each enabled tier. Shared Console/TTY draft guidance remains separate
from released pin adoption and runtime conformance. No kernel, companion, package,
standards-adoption or release gate is closed by this documentation acceptance.

References: [ncurses build options](https://invisible-island.net/ncurses/INSTALL.html)
support application-library/data separation and wide-character configuration; the
upstream libtsm/vte/libseat references explain component scope, not Aether portability,
security, native execution or performance.
