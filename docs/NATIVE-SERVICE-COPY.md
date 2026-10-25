# Checked native input copies

Experimental bounded correctness qualification,2026-10-05. One private owner-bound
helper copies mask8-byte and thread64/96-byte input into kernel-local arrays using
separately checked4 KiB fragments. It rejects overflow and unreadable later pages
before admission/mask/output effects. An8-byte output checks writable endpoints
before the existing fragmented write; input/output overlap remains supported under
IF-clear owner serialization. No ABI/SDK, rights, quota, backing or released pin
change. This removes repeated mapping lookup without a general VM/copy framework.

[Evidence and reproduction](evidence/native-service-copy-2026-10-05/README.md):
final attempt5 has eleven passing fresh correctness/control cases and one blocked
repeated-service deadline. Cross-page alias, readonly/no-access page, wrap, actual
musl descriptor EFAULT/EAGAIN, unchanged failed outputs/resources and DF-set traps
are covered. Initial native mask inheritance is tested before musl restoration.
Selected maintained memory/pair/lifecycle/stack/signal regressions cover190 fresh
targets; full137 host checks, pins/workflow and scoped gates are recorded separately.
The packet remains partial because repeated full dynamic service replacement
exceeds30 seconds; this change does not close that stress gate or prove its cause.

Use a fresh owned root for packet `sdk-setup.py`, `qualify.py 1`, `regressions.py`
and `zig build test`. `checks.py` audits the original five-attempt tree; see the
packet's documented reproduction/ownership distinction. All
attempts/raw logs/source/tool/SDK snapshots are retained and read back before owned
duplicate cleanup. No immutable older evidence or sibling files are rewritten.

Native progress cost,281-lifetime engine workload, production helper sizing,
providers/identity/configuration and calibrated clocks precede full engine runtime
qualification. Public process-mask consumer/SDK reader and assembled serial-shell,
filesystem/package R1 acceptance remain open. This bounded implementation is not
a general POSIX or production-port adoption.


Subsequent qualification,2026-10-05: [owner-local mapping pin validation](NATIVE-SERVICE-PINS.md)
closes selected repeated-service and four-round progress under the same watchdog,
retaining every pin. This supersedes those pending stress results at a newer
kernel revision; the original sealed packet remains unchanged and no broader
engine/production/consumer acceptance follows.
