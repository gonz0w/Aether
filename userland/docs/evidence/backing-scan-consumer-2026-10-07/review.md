# UL-003/015/081 full backing consumer review

Requirement before execution: test the prepared exact word-verification expression
at the service runtime's full8192-page/32MiB geometry with first, word/page boundary,
middle and final-byte dirtiness. Each dirty case must exit91 at its page before
any acceptance; clean scan must visit8192 pages. Deliberate last-word and last-page
omissions must expose false acceptance. This is host boundary coverage, not native
cleanup, timing, timeout attribution, device quiescence or pool acceptance.

Use one simple generated Zig host scaffold around the unchanged selected expression;
no alternate runtime/kernel verifier or sibling changes. Capture source/tool/stdlib
before consuming them. Zig0.16.0 Debug host build (macOS arm64), compile60s/run30s
owned process bounds, fixed environment and private build/cache roots. Preserve
all attempts and compact commands/outputs/receipts; remove generated binaries/caches
after readback. Two actual Python interpreters check source/receipt scope and trace
controls. Quality/published pins, actual syntax, Zig format and whitespace required.
Applicable Foundations E/O/I, Distribution NC/OB/FS and approved TD/TC/TE/CP/Zig.
Original tooling BSD-2-Clause, captured bytes/notices unchanged. Existing owned
helper reused without edits. Independent reader deferred; owner review pending.

Simplicity: choose a full-size host scaffold and explicit dirty offsets rather than
another native VM/kernel build. The existing two-page exhaustive owner witness
covers individual bit/word positions; this adds maximum geometry and bounds.
No obsolete compatibility path is removed. Native execution is the next owner gate.

Actual technical review by Codex: the unchanged expression covers aligned u64 words
inside every4096-byte page, with one require per page. At full32MiB clean8192 and
18 dirty boundaries pass; two truncated controls expose false acceptance. This
complements the owner's exhaustive two-page16384 dirty-bit coverage without
repeating it. Current cleanup oracle rejects70 controls on both actual Python
interpreters. Three prior decoder gaps remain; owner proposal pending. Captured
successful creator is historical, later failed pair remains failed and importer
not started. No attribution, native measurement or independent reader approval.
All child exits and owned cleanup verified; final source/binary hashes read back.
