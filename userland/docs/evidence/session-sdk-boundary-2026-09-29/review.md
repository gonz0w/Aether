# UL-081 / UL-007 supported SDK boundary audit

Scope: inspect the accepted private serial link closure, preserve all prior pins,
and define one future supported boundary. Reuse accepted169-case native evidence
only for the exact baseline bytes; new checks are static linking/provider checks.
No maintained runtime/UL-058 behavior change, SDK installation or sibling edit.

Read quality PROCESS/change-review, UL-081 triage, architecture and current serial
source review. Foundations O/I/E, Coding CP and Testing TD/TC/TE apply. Use unchanged
owned runner: absolute tools,30-second commands,16MiB streams, explicit cwd/env and
fresh private build root. Verify full serial consumer seal, source export, SDK,
archive/index and relevant tool pins before extracting only selected regular files.
Hash every selected link input before execution and after completion. No network.

Reproduce exact accepted serial-parent link with an additional map (no payload
change). Baseline must match accepted whole ELF digest. Independently inspect strong
symbol providers/undefineds; test facade omission, memory-adapter omission, public
fork/wait omission and duplicate facade. Explicit wrapper omission and duplicate
strong definitions must fail. Other omissions may link successfully through stock
libc; record that outcome as fallback exposure, never a native success. No mutant
ELF runs. Preserve attempts, link argv, diagnostics, map and symbol tables.

Select a single opt-in application runtime boundary, with matching ABI/envelope,
bootstrap, process/FD/signal state and musl-private hooks. Current facade and
application wrapper are coupled; packaging an archive alone cannot create shared
runtime authority or general POSIX behavior. Separate author/source review from
independent human review. Pin inputs, namespace policy, unsupported calls and future
acceptance cases before asking owner implementation. Existing masks share kernel
state; do not resurrect a duplicate local signal mask. Follow the approved SE-01–05
questions: simpler stock-libc-only link cannot enforce this private contract; an
explicit bounded runtime extension is chosen over generic compatibility machinery.
No active path removal until consumers and replacement are qualified.

Deliver source-bound audit and candidate SDK integration handoff; update UL-081,
STATE/BACKLOG/ROADMAP/ARCHITECTURE/coverage. Run quality/syntax/whitespace and prior
seal checks. UL-081 assessment may finish; runtime implementation and owner/reader
approval remain incomplete. Stop dependent integration if no matching owner
runtime/SDK delivery exists. SI-07 versioned runtime remains a separate prerequisite.
