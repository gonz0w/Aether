# Directory-only mktemp candidate

This experiment prepares `mktemp -d TEMPLATE` for an Aether application using the
existing filesystem mutation client. A bounded host run exercised the real Toybox
startup, the Rust Client and service, and a typed C provider fixture. It did not
boot an Aether application, access an OpenZFS disk, or qualify a package import.
[Issue #97](https://github.com/gonz0w/Aether/issues/97) owns the live work and
its current review and continuation.

## Contract

The candidate accepts an explicit template under one provisioned home parent.
The full template and every other active argument or environment string have at
most 31 payload bytes under the existing native startup record. A matching prefix
is a label for that provisioned capability; `ROOT`, `CWD` and `TMPDIR` grant no
mutation authority. The parent has home rights 15. The candidate uses mode 0700,
a process-local mask of 0077, checked monotonic time and a positive TLS identity
to generate a name. The name is not a cryptographic secret or a uniqueness
guarantee.

Exactly one MakeDirectory request is attempted. The returned pathname does not
acquire a directory file descriptor. A collision or uncertain mutation does not
retry, reconnect, unlink or roll back a pathname. Typed progress remains available
if output or finalization later fails. The host binding performs Client disconnect
and records both endpoint closes once; repeated finalization uses the cached result.

## Host evidence

On 2026-10-28, the separately selected HOST07 entry completed in 14.126 seconds.
The root-observed process exit was zero, all 105 child groups had known cleanup,
and owned temporary outputs were removed. The compact result identity is
`c4514399054b3478e4f8755187d1b1010ce52dc44f0bffc766f24766e1a9b834`.
A separate evidence review accepted the host result. The process/docs quality
gate is a separate integration prerequisite; issue #97 and the PR retain its exact
current receipt.

The run included eight scripted C cases, a positive repeated-finish case and
nine compiling C omissions; twelve isolated Rust tests and three compiling Rust
omissions; non-mutating format checks and three scoped Clippy checks; and five
separate real-Toybox terminal cases. The latter covered success, collision,
output failure after creation, finalizer failure and invalid clock input. They
used the actual Client/service and a typed C engine fixture. The host clock was
injected and the host TLS identity was observed. These results do not establish
native clock authority, real storage behavior or a usable shell.

Input preparation used the pinned Toybox 0.8.14 archive, a single maintained
source tree and the selected miniconfig. The generated configuration and
preprocessed applet table selected only mktemp, with two recorded support flags.
A separate discovery receipt recorded the used tool and header identities before
the host source freeze. The host SDK, libc, dynamic loader and shared libraries
are not a hermetic runtime closure. [inputs.json](inputs.json) retains the initial
public candidate metadata; its source-only and header-discovery wording describes
that starting lock, not the later private host receipt.

## Reproducing the recorded run

The public [check.py](check.py) is an unselected producer library: direct
invocation exits nonzero and starts no build. Its legacy process helper remains
outside the selected route; see [issue #94](https://github.com/gonz0w/Aether/issues/94).
The successful entry was the owner-selected private `host_producer_07.py` with
source freeze `4ee0a150ac7f745b5d0bd165e9b88a685358677d6e946275a56353eb551e729a`.
That entry and its qualification inputs are not included in the public checkout,
so the result cannot be replayed from this checkout alone. Issue #97 records the
selection, actual outcomes, source identities and review. No later phase starts
automatically.

The selected host entry used one 300-second aggregate, an execution cutoff at
270 seconds, children capped at 60 seconds, 4 MiB per output stream and 16 MiB
compiler files. Sources and inputs stayed frozen. Previous attempts remain
failed: the recorded causes included a strict linker-option error, a masked
finish-order omission, a Rust/Clang loader conflict with preserved intermediate
objects, and two Clippy diagnostics. Their owned outputs were disposed after
known cleanup; compact commands, identities and failure records remain private.

## Native boundary

The ordinary application clock and authenticated namespace bootstrap are not
matched to this candidate. The current clock operation requires a threaded role,
while an ordinary process-app slot is not threaded and its auxv 0xa001 is a
channel endpoint. The provisioned parent, epoch, transport and finalizer also need
a matched application route. [Issue #98](https://github.com/gonz0w/Aether/issues/98)
records the owner-approved contract. Implementation and matched native fit remain
pending; host fixtures do not replace that route or prove a native positive fit.

The intended ordinary-app bounds remain a 1 MiB ELF, 128 image-plus-stack pages,
128 backing pages and 4096 TLS bytes. The stack mapping is 64 KiB with an initial
SP offset of 48 KiB. The larger Zsh profile is not selected. Preserve Toybox and
musl notices and member identities. Original adapter source uses BSD-2-Clause;
the checked helper retains its musl-derived notice.
