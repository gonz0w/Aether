# UL-013 / UL-066 package tr subset

Snapshot current pkg-mgr/mk shell files and sys-init/scripts shell files read-only.
The search is a textual source census, not shell execution or exhaustive dynamic
call discovery. Preserve file hashes and all tr-bearing lines; sibling adoption
is not implied. Userland owns this candidate compatibility record only.

Two observed literal forms: -d [:space:] and -d \\012\\040-\\176. In C locale,
whitespace removes bytes9,10,11,12,13,32; the binding form removes10 and32..126.
Independent byte-filter oracles test all256 bytes and empty input for both pinned
GNU and BusyBox. Add the actual numeric-whitespace shape for each provider: ten
cases total. Require exact output, empty stderr,exit0 and process/container cleanup.
No bindings or sibling scripts are executed, no files installed or changed there.

Reuse RANGE-PLAN runtime pins, owned helpers, licenses, source capture, read-only
inputs/offline512 MiB/32 PIDs/uid65534,15-second children/180-second container.
C locale only; the profile excludes arbitrary operands and Unicode character
processing. Existing /dev/full failure coverage remains linked, not rerun or
claimed as a fresh consumer integration. Record missing locale/error propagation
context as owner follow-ons. Run syntax, ten actual cases and quality. Review
pending; explicit candidate subset does not establish native/package acceptance.
