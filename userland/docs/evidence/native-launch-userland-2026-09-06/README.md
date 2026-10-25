# Native launch framing — UL-058 NB-03

Ten new native cases pass. The complete-frame corpus changes 22 documented fields
one at a time: version/counts, header/entry reserved bytes, command padding,
argument/environment termination and padding, allowlist and unused startup slots.
Each requires exact errno and zero receipt bytes, then the original runner launches
and collects a valid command on the same connection. Both generations complete
with exact output verification and six reclaims. This is 44 extra complete-frame
rejections in one successful native case, not 44 independent boot cases.

Seven parent-live EOF witnesses transmit exactly 0/1/4/16/31/32/383 bytes, close
only the sending endpoint and require broker1100+length/reclaimed0. No terminal
record may appear. The owner's pinned producer checks aliases/positions before
that diagnostic. This is fatal rejection, not reconnect or remote recovery.

The producer's existing allow_launch_version mutation is caught at parent103,
broker970. Its pad_launch_eof mutation is caught at parent104 after draining the
forbidden reply, then broker970. These are isolated compile-time producer controls;
owner source files remain unchanged. Unrelated panics/timeouts cannot pass.

All 27 combined cases, nine original-pin regressions and 21 host/control tests
pass first attempt. Thirteen prior client ELFs remain byte-identical, including
all five legacy clients. Eight new client ELFs pass existing inspections.
The ordinary adapter is unchanged; runner additions compile only with explicit
launch witness flags. Default pins, native ABI and grants remain unchanged.

Exact sources, diffs, corpus, maps, ELF artifacts, serial logs, commands and owned
process cleanup are retained. Large images/checkouts stay in the build roots in
summary.json. The source archive remains bound by the earlier reviewed producer
lock. C formatting and Python grammar pass. NB-04, public carrier/parser, ASan and
independent technical/reader review remain open; this does not complete UL-058.
