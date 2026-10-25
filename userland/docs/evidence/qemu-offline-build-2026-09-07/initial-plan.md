# UL-069 offline full emulator build

Consume the approved CMSPAR patch, pinned QEMU 10.0.11 archive, 103 local Debian
packages and pinned reference image. Verify all 117 retained files before copying;
verify staged archive/deb/patch bytes again. No network in the build container,
no image pull, no host-prefix install, no modification of the original image.

Use the reviewed dash lifecycle adapter unchanged to create/inspect/start/remove
one uniquely labelled owned container and confirm absence. A local build-specific
Client adapter changes only its create arguments: writable disposable root, UID0
for dpkg, 1536 MiB, 128 PIDs, two CPUs, and CHOWN/DAC_OVERRIDE/FOWNER/SETUID/SETGID
capabilities for trusted package maintainer scripts. Retain no-new-privileges and
network=none. Inputs are a read-only private tree; only its output child is a writable
host mount. Package setup cannot install to the host. No privileged container,
host PID/network namespace or additional host mounts.

Install local packages with dpkg in the disposable root. Record installed package
versions, compiler/Meson/Ninja/Python and system identities. Build only x86_64-linux-user
with Clang19, --disable-download and optional features disabled. Two out-of-tree
builds use the same source: baseline first, then apply the exact approved patch and
build candidate. Preserve source before/after hash and both executables. Do not
promote translation tests into PTY acceptance; real terminal controls follow.

Bounds: 20-minute owned start call, two parallel compiler jobs, existing 20-second
lifecycle calls and confirmed cleanup. Host command output remains bounded at16MiB.
This budget is not a speed claim. Retain every attempt and cleanup result, including
install/configure/build failures. No unknown cleanup or missing binary can pass.
Use current Python3.10+ lifecycle/CP profile; qualify actual interpreter only.

Validate exact create-profile transformation with host controls before live use;
run local quality gate and selected build. Original shell uses POSIX sh, set -eu,
explicit paths and checked commands; syntax-check with /bin/sh -n. Preserve QEMU
GPL/LGPL and package notices. This new build tooling needs its own independent
review; prior approval covers the translation patch, not new lifecycle behavior.
