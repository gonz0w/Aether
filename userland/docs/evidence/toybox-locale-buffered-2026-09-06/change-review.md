# UL-067 locale and buffered-output plan

Use the verified standalone cat object closure, reproduce its original ELF, then
link a separate C17 observer/fault wrapper around setlocale, newlocale, uselocale
and read. Record exact startup call order and CODESET at first input read under
LC_ALL=C. Deny setlocale, deny the first newlocale, and deny both newlocale calls;
check exact bytes/status/trace, including whether startup continues. No upstream
patch, fake native API or production behavior change. Unknown trace fails.

Run uninstrumented cat -e with small and multi-buffer input, compare exact output,
and redirect each to Linux /dev/full to exercise real buffered write errors.
Use the pinned local QEMU image, no pull/network/VM lifecycle actions, private
read-only inputs, UID65534,512MiB/32PID,45s case bounds and named cleanup.
Retain every attempt, plan/source/object/tool/ELF hashes and raw output. Require
negative trace/status oracle controls, host UBSan wrapper checks, strict C17
warnings and pinned format, CLI/grammar and local quality gate. Same-task review
is not independent acceptance. Shared E/O/I and CE/CC/CP/TD/TE apply; pins and
upstream notices remain unchanged. No target execution, Unicode conformance,
real locale resource exhaustion, security or packaging claim. UL-067 stays active.
