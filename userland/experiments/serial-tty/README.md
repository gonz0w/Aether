# Bounded serial terminal core

Issue [112](https://github.com/gonz0w/Aether/issues/112) owns this userland prototype.
It is one safe `no_std` Rust terminal policy object with four alias slots, no
allocator or byte queues, and a sixteen-byte read scratch on the stack. The module
creates no kernel capability, POSIX descriptor, wire protocol or service process.
Sys-init keeps admission, supervision and recovery policy. A later reviewed adapter
can host this core in the existing Rust serial owner.

## References and admission

`Terminal::admit` receives a nonzero terminal identity, trusted caller identity and
generation, explicit rights for stdin/stdout/stderr, and an initial supported mode.
The dispatcher must obtain the caller context from its authenticated binding;
a claimed PID or application-provided integer is not authentication. Terminal
identities must distinguish actual owner instances. These constructor arguments
represent existing authority; they do not grant access to a UART.

READ, WRITE and MODE rights are independent of descriptor role. References have
private terminal/caller/alias identities. Every operation checks the current
caller, generation, terminal, live alias serial and required owner-held rights,
including zero-length I/O. `classify` returns the original stdin/stdout/stderr role.
`duplicate` preserves that role and all rights to the same terminal. One duplicate
fits beside the three initial bindings. Closing a reference retires that alias;
it does not hang up the device or close a surviving alias. Reused alias slots get
new serials. Exhaustion rejects without effects; serial increments never wrap.

Owner-only `disconnect` records actual hangup. Owner-only `replace` requires a
newer nonzero caller generation, validates the whole new admission first, and
invalidates all old references and snapshots. It resets the mode/revision and
failure state for that new generation. Physical device cleanup and admission
remain the owner's responsibility, including after the last alias closes.

## Immediate mode and restoration

`ModeRequest` contains `Mode` plus `ApplyWhen`. The only supported settings are:

| Field | Supported value |
| --- | --- |
| canonical, echo, signals, IGNCR, INLCR, OPOST | false |
| VMIN / VTIME | 1 / 0 |
| ICRNL | false preserves CR; true maps each confirmed CR byte to LF |
| apply action | Now |

Other bytes, including LF and control characters, stay exact. Output is unchanged.
Drain and flush reject as unsupported; no empty queue or UART holding-register
observation claims physical drain. This immediate, nonblocking core returns
WouldBlock when empty. Any later blocking POSIX adapter must use its actual wait
contract. This subset does not qualify ZLE's ISIG, canonical input or job control.

A MODE-authorized snapshot records terminal/caller identity, generation, original
mode and expected revision. `apply_now` validates the complete request and snapshot
before effects, increments revision even for a valid idempotent apply, and advances
only that snapshot's expectation. Its saved original mode remains unchanged.
`restore` requires the exact current revision, restores that original mode,
increments revision and consumes the snapshot. Competing changes, replacement,
foreign/stale callers and exhausted revisions reject without partial changes.
Snapshot restoration creates no recovery takeover authority.

## Read and write completion

Each data operation invokes at most one synchronous callback, offering at most
sixteen bytes. There is no prefetch, pump, retry, read-all or write-all loop.
Read uses stack scratch and copies/translates only the confirmed prefix into the
caller's output. Thus a refused/zero-progress read never exposes scratch writes.
Write preserves stdout/stderr role and returns its exact confirmed short count;
the caller still owns the remainder. Zero-length requests validate access and
failure state, then return without invoking transport.

Callbacks return `Completion { count, stop }`. A positive count within the offered
slice wins over Complete, WouldBlock or Interrupted. End can accompany a final
positive prefix: return it first, latch disconnect, and return EOF on later reads.
An owner disconnect blocks writes immediately but does not discard input already
buffered by transport. Reads continue bounded callbacks until that buffer is empty,
then latch EOF. Explicit read End alone certifies the final prefix with no residual
input; output End does not certify input drain.

With zero progress, Complete/WouldBlock mean live-empty WouldBlock; Interrupted,
explicit End/EOF and a known zero-effect negative errno remain distinct. Empty
read requests return `EmptyRequest`, independently of EOF. Nonempty writes after
hangup return `HungUp`; a zero-progress End also establishes hangup.

Unknown effects, oversized counts, invalid errno values, or a positive count paired
with a claimed zero-effect Error fail closed as `UnknownCompletion`. They never
return a successful count or WouldBlock. Every later data operation, including a
zero-length request, stays blocked until owner replacement. The owner must retain
actual replies/outcomes and cleanup obligations across transport loss; this local
module supplies no replay or reconciliation protocol. Callback errors must satisfy
this synchronous completion contract before a native adapter can use them.

## Focused verification

From the system root, with the pinned Rust 1.98.0 toolchain and an owned output
folder supplied by the existing bounded capture helper:

```sh
rustfmt --edition 2024 --check userland/experiments/serial-tty/tty.rs userland/experiments/serial-tty/tty-tests.rs
rustc --edition=2024 -Dwarnings -Dunsafe_op_in_unsafe_fn -Funsafe-code --test userland/experiments/serial-tty/tty.rs -o OUTPUT/tty-tests
OUTPUT/tty-tests --test-threads=1
rustc --edition=2024 -Dwarnings -Dunsafe_op_in_unsafe_fn -Funsafe-code --target=x86_64-unknown-none --crate-type=rlib -Cpanic=abort userland/experiments/serial-tty/tty.rs -o OUTPUT/libserial_tty.rlib
clippy-driver --edition=2024 -Dwarnings -Dunsafe_op_in_unsafe_fn -Funsafe-code --target=x86_64-unknown-none --crate-type=rlib -Cpanic=abort userland/experiments/serial-tty/tty.rs -o OUTPUT/clippy.rlib
clippy-driver --edition=2024 -Dwarnings -Dunsafe_op_in_unsafe_fn -Funsafe-code --test userland/experiments/serial-tty/tty.rs -o OUTPUT/clippy-tests
```

Use one 300-second focused aggregate, children at most 180 seconds, 4 MiB streams
and 16 MiB compiler files. The actual-module tests cover lifecycle, alias/authority
and generation boundaries, short I/O, progress before interruption/backpressure,
mode/restore validation and unknown-completion containment. Selected compiling
guard omissions must fail the same semantic assertions; no missing-module compile
is reported as a prior behavioral red result. Keep compact results and failures,
and remove owned compiler outputs after checking them.

The existing private `userland/docs/quality/check.py` checks unchanged offline
adoption inputs. Public standalone snapshots/checkers remain unavailable under
[PUBLIC-SOURCE](../../../docs/PUBLIC-SOURCE.md); that private pass does not verify
this new README or inventory, which receive separate source/reader review.

Native terminal admission/fit, UART dispatch, C/musl adaptation, real drain,
canonical editing/signals/groups, TERM/data and interactive Zsh remain later gates.
No host result here establishes native TTY, login or R1 acceptance.


## Selected ordinary-app byte probe

[Issue114](https://github.com/gonz0w/Aether/issues/114#issuecomment-6564180472)
selects `native-byte-probe.c` through `AMK_NATIVE_TTY_BYTE_PROBE` in that file and
`../mktemp-directory/native-main.c`. The entry calls `amk_tty_byte_probe` through
the existing target callback, replacing the Toybox callback only for this build.
Do not compile Toybox objects for the probe. The checked helper, native namespace
adapter, musl TLS/clock, FD startup and returning finalizer retain their roles.
The callback copies the admitted template into a local 32-byte buffer before its
single checked directory creation; argv storage need not be writable.

The runtime and owner link select `--cfg native_tty_byte_probe`; build this core
as `--crate-name=serial_tty --crate-type=rlib` and pass its `--extern serial_tty`
to `native_app_runtime`. The admitted app's actual handle/epoch authenticates the
owner-held core caller. The existing process channel and ConsoleRefs route READ0
and WRITE1–2, with no MODE right. Immediate mode preserves every input byte,
including NUL, CR, LF and bytes 128–255. Zero-effect EAGAIN retains the current
request within the original absolute 6000-tick deadline. Unknown completion
contains the owner before a fabricated reply. All three aliases must close
before process-channel EOF. Default builds retain two output aliases/two closes.

The frozen exchange is hex `00411b420d430a447f450146024780ff`. After wrong-direction,
zero-length and raw nonowned-UART denial checks, stdout emits `TTY-BYTE READY\n`.
The app reads and compares 16 bytes, closes stdin and checks its local EBADF,
then emits `TTY-BYTE OUT\n` plus those 16 raw bytes and one framing LF. Stderr
emits `TTY-BYTE ERR\n`, closes and checks EBADF. Stdout emits `TTY-BYTE PASS\n`,
closes and checks EBADF before return 0. Data loops advance only positive confirmed
short counts; zero, negative or malformed progress aborts without retry. Markers
are fixed machine records. PASS requires later normal app/engine terminals,
namespace/FD/raw finalization, reclaim and clean halt before a native success claim.

For focused host checks, compile the existing owner test root both with and
without `--cfg native_tty_byte_probe`. Its selected tests cover actual routing,
binary/short/pending input, three-close settlement, malformed counts and forged
references; its default tests preserve the exact old startup and lifecycle.
Compile `native-main.c` and `native-byte-probe.c` with both
`-DAMK_NATIVE_APP_HOST -DAMK_NATIVE_TTY_BYTE_PROBE`; link `native-byte-tests.c`,
the existing FD units and native stdio test bridge into the `native.rs --test`
root with `--cfg amk_native_host --cfg native_tty_byte_probe`. The new callback
controls explicitly substitute the checked helper and raw trap observations;
they exercise actual C startup, FD ledger, data path and cached finalizer. The
unchanged target/helper bodies and real kernel denials require the target witness.
Use UBSan, existing bounded capture, the 300/180-second aggregate/child ceilings,
4 MiB streams and 16 MiB files. Apply existing Rust/Clippy/C formatting checks and
compile the selected no_std runtime for `x86_64-unknown-none`. Compiling omissions
of unknown-reply containment, CR preservation and either raw denial must fail the
same assertions. No synthetic or host result qualifies native TTY, persistence,
terminal modes, interactive Zsh or login. The changed app and owner need fresh
linked geometry/TLS/stack fit under the existing limits before native execution.
