# Isolated reference emulator correction (UL-069)

The current Linux-QEMU reference loses CMSPAR on write and read. See the
[diagnosis](../../docs/evidence/qemu-termios-2026-09-06/summary.json). This experiment
prepares a separate x86_64-linux-user emulator; current image and failed acceptance
remain intact. No Aether implementation or full POSIX acceptance follows.

## Input checkpoint — 2026-09-06

The existing image contains no C compiler, make, Meson, Ninja, pkg-config or required
development headers. A download-only collector obtained 103 Debian packages
(101,005,780 bytes), including Clang 19.1.7, Meson 1.7.0 and Ninja 1.12.1. This
Clang is a separately pinned Linux-host compiler, distinct from the Clang 21.1.8
used for target musl/candidate binaries. Transitive GCC runtime/development packages
do not select GCC as the emulator compiler.

The first collector failed on apt's sandbox user switch under cap-drop=all. The
retry uses root inside its owned disposable container and fresh private apt-list
and cache directories, retaining cap-drop=all and repository authentication. It
succeeds with download-only mode; no package is installed. An image apt cleanup
hook emits a cache permission warning, retained in stderr; download and subsequent
hash verification succeed. Both containers are removed.

`source.lock.json` pins the QEMU 10.0.11 release archive. `build-inputs.lock.json`
pins every collected file and exact package versions, with the acquisition receipt.
All archive/deb/metadata bytes remain under the locked build paths and must be
retained; copying the recipe alone is insufficient for offline reproduction.
The release contains TARGET_CMSPAR and bundled Meson/pycotap wheels. Source HTTPS
acquisition does not close independent authentication under UL-016.

[Evidence](../../docs/evidence/qemu-build-inputs-2026-09-06/summary.json) retains
all acquisition attempts, input inventory, sources configuration and source review.
The existing runtime image has not changed. This acquisition checkpoint predates
the full build and direct PTY witness below.

## Next step and acceptance

Install only verified local packages into a separate disposable build environment
with network disabled; compile with Clang and QEMU --disable-download, selecting
only x86_64-linux-user. First retain an unpatched source-built control, then the
smallest guarded CMSPAR translation change with original GPL terms. Verify paired
set/read/clear, partial-failure and explicit recovery behavior, then rerun full
GNU/BusyBox consumer suites. Record all build/runtime tools and dependencies.
Do not filter failed options or count source inspection as a runtime pass.

No sibling wait is required. UL-069 remains active; broader source/security,
quality review, native TTY and packaging acceptance remain separate.

## CMSPAR translation patch preparation — 2026-09-07

The pinned cflag table omits CMSPAR; both target-to-host and host-to-target paths
use it. [cmspar.patch](cmspar.patch) adds one row guarded by both definitions.
[Host translation evidence](../../docs/evidence/qemu-cmspar-translation-2026-09-07/README.md)
uses actual upstream functions/non-baud table rows and a deliberately different
synthetic host bit: original and wrong-bit controls reject; patched and either
missing-definition variants pass. Three positive variants each exercise 1024
flag combinations in both directions. Unsupported variants explicitly omit the bit.

Reproduce with `python3 -B experiments/qemu-termios/check-translation.py` from the
repository root after the pinned offline inputs and recorded macOS SDK are present.
The [plan](TRANSLATION-PLAN.md) records scope. Original files and GPL/LGPL notices
remain in private build output; the patch does not relicense QEMU. This is host
translation evidence only. Next: isolated offline unpatched/patched emulator builds,
paired PTY set/read/clear, partial failure and restoration, then full consumer suites.
The existing image and failed terminal acceptance remain unchanged.

## Full build and direct Linux PTY witness — 2026-09-07

[Evidence](../../docs/evidence/qemu-offline-build-2026-09-07/README.md) now retains
complete original/patched offline builds and12 direct PTY cases with exact termios
restoration. All103 installed package versions match pins. Original QEMU reproduces
CMSPAR loss; the patched emulator matches image-native stty for set/read/clear and
partial cmspar+parenb failure. Every created container was removed and absence checked.

Build from the repository root with
`python3 -B experiments/qemu-termios/build.py` after the existing Podman VM is
available. [BUILD-PLAN](BUILD-PLAN.md) describes the writable disposable package
root, limited capabilities and read-only input/private output mounts. No download
or original-image mutation. On this desktop, start the existing VM and run the
live command in the same execution session. Missing image/input/connection stops
the attempt; do not provision replacements or refresh pins automatically.

Run `python3 -B experiments/qemu-termios/run-pty.py build/qemu-build-lshq21vi` for
the retained build. [PTY-PLAN](PTY-PLAN.md) documents the read-only staged GLib/
libatomic runtime, licensing and narrow test scope. Host controls are
`test-build-profile.py`, `test-extract-source.py` and `test-apply-cmspar.py` in this
directory; run each with `python3 -B` from the root. The last consumes the retained
source under build/qemu-translation-j5hf1b1a. Python qualification is limited to
the actual recorded versions; no minimum-series run is inferred.

Next UL-069: full GNU/BusyBox consumer regressions using this exact emulator/runtime
set. Direct PTY success does not erase previous upstream-suite/restoration failures.
New build/runtime review remains pending; translation approval is a separate scope.

## Consumer regressions — 2026-09-07

The maintainer approved the offline builds and twelve direct PTY cases. The new
consumer adapter runs the unchanged GNU shell fixtures with the corrected emulator
and its pinned runtime libraries in read-only, offline containers:

```
python3 -B experiments/qemu-termios/run-consumers.py
python3 -B experiments/qemu-termios/run-common.py build/qemu-consumers-0c7_83ua
python3 -B experiments/qemu-termios/run-upstream.py build/qemu-consumers-0c7_83ua
```

The first command deliberately returns incomplete while the main upstream stty
script leaves changed settings. The option-pair suite now passes with restoration
and all 9,029 traced stty calls retained; its former 188 CMSPAR failures are gone.
GNU common fixtures remain 17/17; BusyBox remains 13/17 with the same four tr
comparison differences. Preserving BusyBox's basename fixed a staging error in
an earlier retained attempt. Stable differences do not qualify that provider.
See [consumer evidence](../../docs/evidence/qemu-consumer-regression-2026-09-07/README.md)
and the [GNU shell](CONSUMER-PLAN.md), [common](COMMON-PLAN.md), and
[upstream](UPSTREAM-PLAN.md) review plans for input, oracle and cleanup boundaries.

## Explicit recovery — 2026-09-07

`python3 -B experiments/qemu-termios/run-recovery.py` verifies and stages the
approved consumer inputs, then measures exact termios/window recovery after the
unchanged main script, exit23, and a timeout. All three restore successfully. An
omitted-restoration control remains false until unconditional final rescue.
All four PTYs close after final readback, process cleanup completes, and the
container is absent. The main script's natural-restoration result remains false.
[Recovery evidence](../../docs/evidence/qemu-recovery-2026-09-07/README.md) and
[review plan](RECOVERY-PLAN.md) preserve the distinction. New recovery review is
pending; this does not qualify native terminal behavior.

The maintainer subsequently approved the recovery slice. UL-069 is closed within
its reference-only scope; see the [approval receipt](../../docs/evidence/qemu-recovery-2026-09-07/maintainer-review.json).
UL-066's legacy BusyBox coverage reuses this runtime through run-legacy.py and
[LEGACY-PLAN.md](LEGACY-PLAN.md), preserving its separate provider acceptance.
