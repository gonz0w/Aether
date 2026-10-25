# Native terminal kind — UL-058 NB-04

Three new native cases pass. Unchanged bytecount produces real output; a link-only
wrapper on its first close(0) triggers normal _exit(134) or __builtin_trap before
closing either inherited alias. The latter is an actual invalid instruction,
not a fabricated result. The parent requires detail134/kind1 or detail134/kind2
respectively, rejects foreign and consumed receipts, observes shared-position
EOF and closes its aliases. The owner independently verifies output and releases
abandoned child aliases. Both cases complete two generations with six reclaims.

The pinned producer's fault_as_exit mutation preserves the actual child fault
record but misreports collection kind. The parent rejects at53 and broker970/
reclaimed0, with no success marker. Numeric134 alone is not a POSIX signal encoding.
The finite parent still exits29; public runner mapping is not implemented here.

All 30 combined native cases, nine original-pin regressions and 21 host/control
checks pass first attempt. Twenty-one previous client ELFs are byte-identical;
four added parent/command variants pass ELF and real-musl inspections. The normal
adapter and bytecount source are unchanged. New runner expectations are opt-in;
default producer pins remain intact. Format and Python grammar checks pass.

NB-01–04 now have scoped native witnesses. Full UL-058 review remains incomplete:
independent technical/reader reviews, complete public startup observation and
broader race/stop/unknown-recovery work remain open. The next UL-059 step is a pure
carrier decoder/CLI selector, then native integration. ASan remains incomplete.
No POSIX process, public CLI, package or sys-init acceptance is claimed.

Sources, diffs, wrapper, maps, artifacts, exact serial records and process cleanup
receipts are retained here. Large images/checkouts remain in the build roots
listed in summary.json. The producer archive is pinned in the prior review bundle.
