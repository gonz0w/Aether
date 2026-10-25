# UL-066 legacy BusyBox tr review

Close the five unrun pinned BusyBox1.38.0 legacy tr scripts as a Linux reference
coverage slice. No provider/native promotion. Quality CP/TD/TE and Foundations
O/I/E apply; public presentation and shared standards unchanged. Original helpers
BSD-2-Clause; extracted upstream tests retain README/COPYING terms.

Use exact approved consumer emulator/libraries and pinned GNU/BusyBox binaries.
Verify source archive, runtime and binary hashes before launch. Extract only
named regular test/notice members; no upstream editing. Preserve executable
basenames, explicit BusyBox applet argv, C locale, image echo/diff and /bin/sh.
Use upstream's sh -x -e convention in five separate private scratch directories.
GNU tr is the comparison provider, not image tr. Require each normal script exit0;
add independent exact ROT13 stdout for the non-gnu script. Record comparative
log bytes, argv, exit/stdout/stderr and cleanup. Any difference remains incomplete.

Repeat each with a busybox wrapper returning99; all five must reject. Never count
nonexecution or missing input as a passing fixture. Runtime helpers are pinned by
image; no package installation. Owned unchanged process/container helpers impose
15-second child and180-second guest bounds,512 MiB,32 PIDs,read-only inputs,
no capabilities/network,uid65534. Private tmpfs logs disappear with container only
after final JSON capture. Verify all groups cleaned and container absent.

Run syntax, ten live cases and quality gate. Capture all attempts and hashes.
New adapter technical review and reader walkthrough pending. This slice does not
close BusyBox's four known comparison differences, source trust, locales, static
fault injection or native terminal acceptance. Update UL-066, STATE, README and
quality coverage; UL-069 stays done for its earlier approved scope.
