# UL-069 direct PTY acceptance slice

After verified full baseline/candidate builds, run the same pinned GNU9.11 static
stty under each emulator and image-native stty as a Linux reference. Use the existing
read-only, network-disabled, unprivileged container lifecycle unchanged. Stage only
verified emulator/stty/helper sources, with read-only inputs and private /scratch.
The image's /usr/local/bin/python3 runs the guest probe; no host PTY is modified.

On separate owned PTYs test CMSPAR set, host-seeded readback, clear, and combined
cmspar+parenb partial failure. Baseline must exhibit the diagnosed dropped bit;
candidate and host reference must preserve it. Require actual host termios bit
observations, exact exits and the semantic partial-failure diagnostic. Missing
loader/library/tool, timeout or boot failure is not a semantic rejection. Finally
restore full original termios and verify exact equality before closing endpoints.

Use existing owned-process helper for each stty call via -F /dev/pts/N: 10 seconds,
1MiB output bound, exact argv/environment/exit/cleanup. Container budget 120 seconds;
16MiB total process receipt bound and verified container absence. Twelve planned
cases, four per provider; no frontend parsing or terminal capability claim beyond
the observed Linux PTYs. GNU/BusyBox upstream suites remain a separate follow-on.

Pin full build summary, both QEMU artifacts, GNU stty receipt/binary, image and
helper source identities before staging. No sibling/current-image modification,
new shared semantics or source authentication. Evidence includes all attempts,
restoration failures and new host orchestration/source hashes. Local quality gate
and actual target outcomes required; independent new build/runtime review pending.

The base image lacks the built emulator's GLib runtime. Stage the exact regular
shared object and copyright from the already-pinned libglib2.0-0t64 Debian package
using bounded owned ar extraction and named tar members; record payload hashes.
Set LD_LIBRARY_PATH=/inputs/lib only for the two emulators. Keep image libc/libm
and any transitive dependencies explicit through the pinned image; do not install
or alter the reference image. Missing libraries remain infrastructure failure,
never the expected CMSPAR/partial-operation rejection.

GLib also needs libatomic.so.1, absent from the base image. Stage that exact
regular object from pinned libatomic1_14.2.0-19; its package links copyright to
gcc-14-base in the pinned image. Retain that actual notice in the guest report.
Other loader/libc/libm/PCRE dependencies remain image-owned. Both missing-library
attempts are retained as infrastructure failures with restored PTYs and cleanup.
