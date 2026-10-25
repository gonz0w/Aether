# Pre-import SDK consumer link evidence

Initial behavioral attempt passed in build/sdk-consumer-xpazronw. The subsequent
format check rejected the multiline short function. Applied the pinned formatter
and reran all checks: final source passes in build/sdk-consumer-xjmfe2v3. Both
source-bound attempts are retained. The captured one-shot driver
copies and verifies all 231 SDK inputs from the owner's unregistered candidate,
builds strict C17 probe.c, and links strlen from explicit libc.a. Missing headers
fail with the stddef.h diagnostic; omitted libc fails with undefined strlen.
Neither failure publishes the requested output. ELF64 x86-64 inspection finds no
unresolved symbols, INTERP or DYNAMIC segment. Every child records complete cleanup.
No resulting code executes, and no package state or sibling file was changed.

The attempt directory retains exact source/plan hashes, tool identities, argv,
environment and raw streams. Binaries stay under the named build root. Pinned
clang-format dry-run and local quality gate pass. This is not ASan qualification,
C startup, adapter closure or native acceptance. Real export/import has not yet
been delivered; SDK-05 remains NOT RUN for an imported package. The maintainer
and independent technical review remain pending. See PLAN.md and the consumer
README for follow-ons. UL-005 stays active.
