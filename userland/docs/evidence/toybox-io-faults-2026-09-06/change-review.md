# UL-067 I/O fault experiment plan

Relink the verified standalone cat objects with a first-party C17 link-time test
wrapper for read/write/close. Do not change upstream source, retained objects or
native APIs. Use pinned Clang/musl/LLD, private build roots and owned bounded
processes. Link-time injection observes Toybox's external calls; it does not
interpose libc-internal stdio calls or emulate kernel signals.

Exercise baseline copying, short reads, short writes, read EINTR, write EINTR,
write error after a committed prefix and filename close error. Exact byte/status
oracles and required injection markers must distinguish a missing fault from a
passing test. Close injection performs the real close then reports EIO; it tests
return handling, not leaked descriptors or ambiguous remote close. Wrong status
and missing-marker controls must fail acceptance. Keep all attempts and source,
tool, object, plan and artifact hashes. Use the existing pinned QEMU Linux image,
no network/pull/VM startup, 45-second case bounds and exact-name container cleanup.

O/I/E, CE/CP/C and TD/TE apply; original code is BSD-2-Clause and upstream notices
stay intact. Check C17 warnings and pinned format; use a host UBSan wrapper control
where compatible. Quality gate and Python grammar checks required. Record actual
technical review; independent review remains pending. Locale startup tests are the
next separate slice; this phase does not close UL-067 or qualify a native port.
