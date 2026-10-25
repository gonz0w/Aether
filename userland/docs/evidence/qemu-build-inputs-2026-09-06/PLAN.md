# UL-069 isolated reference emulator correction

Build a separate x86_64-linux-user QEMU 10.0.11 using Clang in a new private Linux
build environment. Preserve existing pinned image and candidate binaries. First
collect source and build dependencies without executing downloaded packages;
record exact archive digests, package versions and repository verification logs.
Subsequent install/build must consume those pinned bytes offline. No host-prefix
installation, sibling edits or native ABI change. Follow Foundations E, approved
CP/CD, TD/TE, licensing and local quality workflow. Upstream changes retain GPL.

Current image lacks compiler, make, meson, ninja, pkg-config and development headers.
Use an owned disposable container for apt metadata and download-only acquisition:
240-second budget, 2 GiB/128 PIDs, no added capabilities, private output root.
Repository metadata checks must succeed; never disable authentication. Source
HTTPS acquisition alone is not independent source authentication (UL-016).
Retain all attempts and cleanup. Pin before extracting or installing dependencies.

Build only the Linux user x86-64 emulator, with --disable-download and optional
system/tools/docs features disabled. First reproduce missing CMSPAR in an unpatched
source-built control, then apply the smallest reviewed translation-table change
and rerun set/read/clear, partial-failure and restoration controls. Full GNU and
BusyBox consumer regressions follow. No failed parity waiver or manufactured
successful no-op. Source/API research is not a runtime pass. UL-069 stays active
until corrected tool provenance and all affected runtime evidence are retained.

Initial download-only attempt failed because apt's _apt user switch needs a
capability deliberately absent from this container. Retain status 100 and logs.
Use root only inside the disposable collector with APT::Sandbox::User=root and
fresh private apt-list/cache directories; retain cap-drop=all and authentication.
No package maintainer script executes during download-only acquisition.
