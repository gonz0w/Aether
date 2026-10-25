# UL-007/081/082 ABI29 client candidate review

Plan before code, 2026-10-21. Requirement: remove the demonstrated six-domain
client mismatch without pretending that ABI24 clients work in AENFS003/ABI29.
This is a private proposed client input, not an accepted dispatcher or SDK pin.
Userland owns the assigned runtime; Aether owns native authority and sys-init
owns matching admission/dispatch. No sibling implementation or guest run.

Apply O-01–05, I-01–06, E-01–08, CC-01–04, TD-01–03 and SE-01–05. Select shell1,
children2–4, reserve5, exclude engine0/owner6. Keep epochs1–15 and shell1–3,
three children, finite lifetime and all descriptor/pipe/transport bounds. A
versioned 32-byte greeting must bind actual native PID/PPID and memory auxv;
labels alone never authorize. No frame/output state is published on rejection.
Owner-issued endpoints and existing trap checks remain required. Unknown
transport stops; no replay, polling fallback or synthesized cleanup.

Implement an explicitly selected source/object candidate with a small pure
identity decoder and actual runtime/application call sites. Existing builders
continue to reject ABI29 until full matched component/CRT/link and owner review.
Preserve default profile behavior and sealed artifacts. Source snapshots bind
the old runtime and sibling contract observations before changes.

Tests: strict C17 host decoder with literal native PID examples, full bounded
slot/epoch checks, truncated/foreign/wrong-parent/wrong-memory failures and
unchanged output; compiling semantic omissions; pinned cross-compile both
runtime/application variants and legacy objects, compare legacy objects from
before sources, check new header formatting; local quality gate. Host decoder
tests do not execute channel/fork/exec/FD/native enforcement. Compile is not link
or resource fit. Processes use the unchanged owned runner, clean environment,
60s per compile/30s execution, 16MiB streams and build-only output. Exact tools,
flags, headers and all attempts will be retained. BSD-2-Clause original files;
vendored sources/notices remain unchanged. No new dependency.

Simpler alternative: change 6 to 7 and shift roles. Insufficient because it can
mix peers and misses parent-only branches and role provenance. Choose one
explicit candidate selector and versioned identity boundary. Remove nothing now:
ABI24 consumers remain supported; avoid a role registry or new broker.

Technical assessment is by the implementing agent; independent technical and
reader review are pending. Native copy/exec/wait/FD/TTY, immutable filesystem
loading, real persistent shell command, matched AF07 sys-init selection and
resource-fit witnesses remain required. UL-007/081/082 and M3/R1 stay open.

Final assessment: current/minimum Python runs both pass the full selection, with
identical four candidate objects and eight before/current legacy comparisons.
Strict pure decoder diagnostics/format/UBSan and nine compiling omissions pass.
Runtime/application builds use retained GNU assembly, explicit _GNU_SOURCE and
musl headers before Clang freestanding fallback; no full ISO-C claim for that
existing boundary. Both profiles retain original legacy expressions after the
comparison caught real scheduling differences. Default native objects match,
not a whole ELF or ABI29 runtime witness. Source/object delivery has29 members,
seal4bd1290f28fb38b14554003b804d6dc5992606cef5c64785fdcfeab961c8c3ce.
Quality/pins/inventory and whitespace pass with complete owned child cleanup.
All761 AF07 operational producer inputs match; no local oracle replay/native
attempt. Seven new qualification roots were compacted/read back before removal:
16025105 logical bytes removed,3197535 archive bytes retained (physical disk
reclamation not measured). The separate postflight root was also archived/read
back before removal. Actual independent reviews remain pending. Next full client
link/fit, filesystem FD/executable translation and matching owner/native input
are concrete follow-ons, not completed or implicitly authorized sibling edits.
