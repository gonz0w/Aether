# UL-067 native SDK closure audit plan

Read-only source/archive audit and documentation. Verify the exact strict native
SDK inventory/receipt used by command-runner against its native-stdio-files pin;
verify selected musl sources against the pinned release archive and native syscall
header against the recorded transformation. Snapshot current consumer and owner
contracts. Map startup/locale/stdio/exit to real SDK paths, distinguish built-in
locale selection from injected denial, and recommend a narrow termination seam.

No native linking/execution, libc/Toybox patch, sibling edit, pin update or new
shared standard. Reuse reference findings only within their recorded scope.
E/O/I and DW/DS/TD/TE apply. Validate hashes, source anchors, links and quality gate;
record omissions and pending independent/owner review. Original prose is BSD-2-Clause;
retain upstream copyright/source bytes verbatim. UL-067 remains active.
