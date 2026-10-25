# UL-067 combined Toybox Linux-reference plan

Relink the pinned standalone cat closure, first reproducing its original ELF.
A separate fixture wraps main/umask/read/write/fflush/_exit and replaces only
musl __stdio_write's writev call with the private vector/session bridge. This is
link-time Linux instrumentation, not the selected native _xexit patch. Initialize
explicit mask0077 before actual Toybox startup, observe save/restore and upstream
flush, then invoke session finalization. All scalar/stdout/diagnostic writes share
state. A duplicated stderr observer records bounded lifecycle facts after logical
roles close; that fixture authority is not a proposed native role.

Test exact empty/binary copy, actual buffered cat -e, committed-prefix/lost ACK,
known/unknown close and failed cleanup diagnostic, invalid mask initialization.
Require exact exit/output/observer facts, zero callbacks after poison, real flush
before close, mask restoration and no successful unsupported startup. Preserve
original reference bytes. Add semantic mutant/oracle controls and retain every
attempt, object/source/SDK/tool/patch/ELF identity plus logs. Existing pinned local
QEMU image, no pull/network/VM start, read-only unprivileged container,512MiB/32PID,
60-second bounded processes and exact-name cleanup. Strict C17, format, CLI/grammar,
quality gate. Reuse unchanged host-component UBSan; Linux sanitizer unavailable.
O/I/E and CE/CC/TD/TE apply; original fixture BSD-2-Clause; upstream notices intact.
Native CAT cases and independent review remain open.
