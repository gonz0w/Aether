# UL-005 pre-import consumer link plan

Prepare a minimal libc string consumer against an isolated copy of the exact
owner-staged SDK. No C startup, adapter or native execution claim. The real SDK
transport bundle is absent; these results do not close SDK-05. Original BSD-2-Clause
C17 source, pinned Clang/LLD and readelf/nm; no new dependencies or sibling writes.
Foundations E-01–08 and quality TD/TE/CC/CP apply. Keep package machinery with owner.

Positive: strict C17 freestanding object uses SDK headers and links strlen from
explicit libc.a into static ELF64 x86-64 with sdk_probe entry. Inspect no undefined
symbols, no interpreter or dynamic segment. Missing SDK headers and omitted libc
must produce specific diagnostics and no successful artifact. Use -nostdinc,
-nostdlib, empty sysroot and clean environment. No fake native hooks to make linking
succeed. Record exact argv/tool/source/SDK hashes and bounded process cleanup.

Each command 30 seconds with existing process.py output/cleanup bounds. Stage copy
must match all 231 pinned bytes/modes. Format check and quality gate. Repeat against
real imported SDK only after owner returns its package/descriptor/receipt evidence.
Independent review, real startup/adapter closure, SDK-07 and native SDK-08 stay open.
