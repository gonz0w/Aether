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
are not a hermetic runtime closure. [inputs.json](inputs.json) records the current
source inventory and matched one-app host composition. The selected native app
and owner inputs have now been linked for the one-app experiment. Full application
stack, heap, TLS and backing sufficiency remain with
[issue #97](https://github.com/gonz0w/Aether/issues/97). Earlier private run locks
and receipts retain their original input identities; current metadata does not
select an execution entry.

The selected one-app adapter host family completed on 2026-10-29 in 53.288
seconds with exit zero, 144 known-clean child processes and owned outputs removed.
Its result identity is
`fd55aca6574bd3fdac5670e824eb3fed8feae551e3a517760f36ffbcc9158531`;
a separate peer evidence review is
`527258c3fe1f1c8c00b035cc3b84306b51aef4c4e87cb7eb946bb629ad09a984`.
It exercised 16 namespace cases and 14 normal plus seven isolated fatal app cases
in both debug and optimized builds, seven compiling semantic omissions, C
finalizer/stdio checks and the five real Toybox compatibility cases. The
[test definitions](native-tests.rs), [stdio fixture](native-stdio-tests.c),
[namespace cases](namespace-tests.rs) and [C cases](host-tests.c) identify the
selected sources; they are not execution receipts. The
[app binding](native.rs) and [C startup glue](native-main.c) are the corresponding
one-app sources. Issue #100 records exact source and tool identities and the
separate review. These are host results; native execution and fit remain open.

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

The one-app host checks used the separately selected private `owner_host_06.py`,
`legacy_host_02.py` and `app_host_09.py` entries. Each used its own fixed
300-second aggregate and reviewed source freeze. Issue #100 records the exact
outcomes and peer reviews. These entries and their qualification inputs
are not included in the public checkout; the public `check.py` and root `AT-HOST`
do not run the selected one-app consumer checks.

## Native boundary

The accepted [kernel extension](../../../docs/NATIVE-LAUNCH.md#ordinary-one-app-namespace-launch)
supplies the ordinary app record at auxv0xa003 and the separate lifetime clock
grant0x28012. Auxv0xa001 remains the process channel endpoint; it is never a
clock or thread grant. [Issue100](https://github.com/gonz0w/Aether/issues/100)
owns the matched native adapters under the approved
[issue98](https://github.com/gonz0w/Aether/issues/98) contract. The selected
native app and owner inputs and the positive source and linked path have separate
review under issue #100. The selected link places the existing zero-initialized
`.tbss` after `.data`, so the TLS view lies within one writable LOAD as the
unchanged kernel requires.

The current kernel parser, layout and backing checks accepted the linked app in
an offline host probe. The ELF is 865,344 bytes; its image plus fixed stack uses
47 of the ordinary 128 backing pages, leaving 81 pages available. These checks do
not establish later heap or stack demand. Issue #97 owns whole-app sufficiency and
the matched native handoff. Host and offline checks do not establish a native run,
filesystem export or a usable shell.

`amk_with_native_namespace` is additive to the existing host entry. Its required
verifier borrows the same separate callback state and runs through actual
Client::disconnect_checked after the validated ACK, before both raw closes.
Only the selected native verifier's actual EOF then nonempty-write EPIPE satisfies
that contract; a yield or successful default callback is insufficient. The
namespace unit fixture substitutes this observation solely to check ordering and
error retention. Matched host checks exercise the app's verifier with controlled
trap results; native channel quiescence still needs target evidence. Legacy
`amk_with_namespace` retains its disconnect semantics and C ABI.

App finalization flushes and inspects both streams, finishes namespace while its
borrow is live, then descriptors, independently caches raw closes and clears TLS
before terminal exit. Native FD mask-restore failure has a lower fatal path:
the selected callback uses a disjoint fixed four-capability close ledger, counts
the two process closes already attempted by actual aefd_native_leave, closes only
remaining owned ends and exits125 once. It never reenters Client/FD finish or
performs another mask/clock/wait call. Existing legacy callbacks are unchanged.

The intended ordinary-app bounds remain a 1 MiB ELF, 128 image-plus-stack pages,
128 backing pages and 4096 TLS bytes. The stack mapping is 64 KiB with an initial
SP offset of 48 KiB. The larger Zsh profile is not selected. Preserve Toybox and
musl notices and member identities. Original adapter source uses BSD-2-Clause;
the checked helper retains its musl-derived notice.
