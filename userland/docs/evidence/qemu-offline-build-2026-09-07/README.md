# UL-069 full emulator build and direct PTY witness

Two QEMU 10.0.11 x86_64-linux-user emulators were built offline with Debian Clang
19.1.7 in a separate disposable container: original source, then the approved
CMSPAR patch. All 103 installed package versions match the retained input pins.
The original reference image remains unchanged. These are Linux AArch64 executables
that emulate Linux x86-64; this is not Aether native terminal acceptance.

[Build summary](build-summary.json) binds source, patch, staged input, compiler
package and artifact identities; [baseline](baseline/version.txt) and
[patched](patched/version.txt) version output confirms execution in the build guest.
[Installed packages](installed-packages.txt) and [verification](verification.json)
record the complete checks and all attempts. Source before/after hashes are retained.
The inspected build configuration has no network, 1536 MiB, 128 PIDs and two CPUs,
only the five planned package-setup capabilities, read-only inputs and one writable
private output mount. This verifies configuration, not a measured resource-stress
bound. [Inspection](build-inspection.json), [build plan](BUILD-PLAN.md).

## Actual Linux PTY results

[All twelve cases](pty-results.json) pass: four each for original QEMU, patched
QEMU and image-native stty, using the same pinned GNU9.11 static stty under both
emulators. Baseline set fails and seeded readback loses CMSPAR as expected. The
patched emulator agrees with the host reference on set/read/clear and on partial
failure of cmspar+parenb: CMSPAR persists while unsupported PARENB does not. All
operations have complete process receipts, and all twelve PTYs restore the exact
original termios state before closure. The baseline is a negative control, not a
qualified CMSPAR provider. [PTY summary](pty-summary.json), [plan](PTY-PLAN.md).

The build-linked GLib and libatomic objects were staged read-only from the same
pinned Debian packages after two honest missing-library failures. Other runtime
libraries remain provided by the pinned image. [GLib notice](GLib-copyright.txt)
and [libatomic's image-owned notice](libatomic-image-copyright.txt) are retained.
No library was installed into the reference image. QEMU and dependency notices
remain under their original terms; new helper source is BSD-2-Clause.

## Retained failures and controls

The attempt inventory in [verification](verification.json) links the private build
roots and copied [attempt records](attempts/). Failures are preserved: unavailable
VM, dpkg pre-dependency ordering, empty APT cache under --no-download, missing xz,
rejected absolute firmware link, missing patch executable after successful baseline
build, then the two missing runtime libraries. Every created container has observed
absence; the first disconnected attempt created none. VM startup and live commands
were kept in one execution session after the separate startup session lost its VM.

The final build uses a populated private APT cache with --no-download, installed
Python extraction with strict data_filter and documented firmware exclusion, and
an exact-source/exact-diff patch helper. Host controls verify exact create-profile
changes and restriction-drift rejection, selected unsafe-link rejection, and
changed-source/patch rejection without mutation. [Profile](profile.log),
[extraction](extraction.log), [patch controls](patch-controls.log),
[shell syntax](shell-syntax.log), [quality](quality.log).

The translation patch's prior maintainer approval is recorded in the earlier
translation evidence. The maintainer has now approved this build orchestration/runtime slice; the
[review receipt](maintainer-review.json) binds the statement and verified source hashes.
Full GNU/BusyBox consumer suites, broader terminal recovery, source authentication
and native TTY qualification remain open. Next: rerun those consumer suites with
this exact emulator/runtime set, preserving their existing failure/restoration oracles.
