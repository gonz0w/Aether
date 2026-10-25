# Backlog and open questions

> Public snapshot: read-only historical record. Apply [root PROJECT](../../PROJECT.md#public-onboarding-cutover).
> After verified onboarding/migration, [GitHub Issues](https://github.com/gonz0w/Aether/issues)
> alone own live work, priority, status, dependencies and continuation. Before that
> cutover, only the approved onboarding bootstrap record selects its operation.
> All text below, including old routing, priority and next-action instructions,
> preserves the accepted-base history; none is an active public assignment.
> Stable IDs/contracts remain useful. Excluded local qualification receipts are
> not made available for replay by retaining these summaries or hashes.

## Historical body — accepted-source snapshot

2026-10-22 UL-007/081/082: [real TLS shell relink](../docs/proposals/FS-FORK-TLS.md) corrects
stage81's missing PT_TLS defect. A checked initialized four-byte C17 TLS object
survives the full link; Aether's unchanged actual ELF parser accepts the279568-byte
shell under default limits (79/128 pages including16 stack pages).1010 stage cases/
nine controls, frame5847, default/opt-in libc78 each and seven parser tests pass on
minimum/current Python. Native execution/whole peak fit and matching sys-init
transaction/owner/reader/full UL/M3/R1 remain open; old sealed bytes stay fixed.

2026-10-22 UL-007/081/082: [authoritative file view v1](../docs/proposals/FS-FILE-VIEW.md) now
exports exact remote FILE presence/cloexec from the sole ProcessFiles ledger,
without source calls or mutation.31 process tests/13 controls plus borrow/compiler
and external host/target checks pass; default remote regressions pass. This supplies
sys-init0202/BG-071's requested input. BG-069/070 still require owner consumption,
exact pre-copy file/stream comparison, complete native transaction/settlement,
whole fit and fresh Aether witnesses. Full UL/M3/R1 and owner/reader remain open.

2026-10-22 UL-007/081/082: [armed fork stage/child constructor](../docs/proposals/FS-FORK-STAGE.md)
now passes1008 host cases/seven controls,5847 frame/78 default libc regressions
and full pinned dash32/CRT/libc/public-fork/copy_rebind static link. One5040-byte
boot aggregate, old4952 default unchanged; native park, child quarantine/auxv
rebind/reconstruction and context-ready are real selected source components.
Build/host evidence only. Matching sys-init BG-069 framing/source/refusal/gate
selection and BG-070 owner transaction/settlement/readiness/shutdown are the next
concrete block. Whole fit/native commands/errors/continued parent/wait/cleanup
follow; immutable exec/public dup2/full UL/M3/R1/owner and reader remain open.

2026-10-22 UL-007/081/082: [fork-frame/child predicate candidate](../docs/proposals/FS-FORK-FRAME.md)
consumes Aether's selected serialized ordering and proposed304/32-byte framing.
5847 pure host cases/eight controls, target two-object relocatable link. Request/
reply/ready/sequence and fresh child-startup correspondence only; no native copy,
armed constructor/TLS repair/stage or selected sys-init dispatcher. BG-069 matching
wire/source-label/exclusion agreement and BG-070 composition/full link/fit/native
witnesses remain. Preserve existing pins/APIs/evidence and full UL/M3/R1 open gates.

2026-10-22 UL-007/081/082: [serialized file inheritance v1](../docs/proposals/FS-SERIALIZED-COPY.md)
adds exclusive local file-ledger access across native-copy observation and local
clone. Existing frozen API remains unchanged.26 host tests/ten semantic controls,
borrow-reentry compile rejection and external host/target consumer checks qualify
only the local library. Sys-init BG-069 still needs wire/stream admission/child
transition agreement; BG-070 actual composition/full-link/fit/native cases follow.
No complete fork stage/native readiness or full UL/M3/R1 completion is claimed.

2026-10-22 UL-007/081/082: [libc bridge/link boundary](../docs/proposals/FS-FD-LIBC.md)
completes actual FD/start/wait/exit entry points and BSS context.78 new/five new
controls plus retained803/175/193/482 cases/23 controls. Target17 objects and full
pinned dash32/CRT/libc/public-fork link stop only at __aether_fork_stage. Current
native path waits for matching authenticated128-map FD-copy/child-rebind/failure
transaction; old64-byte stage cannot preserve required state. Sys-init0200 startup
producer exists. Public dup2/full native/POSIX/M3/R1 remain incomplete; no fallback.

2026-10-22 UL-007/081/082: [single greeting consumer](../docs/proposals/FS-FD-STARTUP.md)
proposes AEFDB001/version1/304 bytes and implements native identity checks,
tagged table/source/history admission, early header rejection, single publication
and terminal failed-start cleanup.803 new startup cases/five controls; retain175
context+193 native-call+482 live C/Rust cases/eighteen controls. Target14 objects/
layout only. Next wire libc/shell entry, new process snapshot/copy/exec/rebind and
immutable/failed-exec/fit with matching owner proposal review/native dispatcher.
No default/profile selection, sibling edit or native acceptance. Full ULs remain open.

2026-10-22 UL-007/081/082: [placed context batch](../docs/proposals/FS-FD-CONTEXT.md)
adds startup table/source cross-validation, one context/workspace, automatic whole-
operation guards and cached terminal reporting.175 new context/193 prior native-
call scenarios,482 live C/Rust cases and six new/twelve retained controls; twelve
production target objects/relocatable link plus separate layout inspection. Old
ABI29 shell/table/copy/exec protocols remain unchanged. Next explicit selected
shell/startup adapter, source/identity rebind, immutable/failed-exec preservation,
full placement/fit and matched dispatcher/native witness. Full UL/M3/R1 stay open.

2026-10-22 UL-007/081/082: [native adapter batch](../docs/proposals/FS-FD-NATIVE.md)
supplies channel/stream/pipe/guard implementations:193 native-call host scenarios,
unchanged482 C/Rust cases, four new/eight retained controls and eleven target objects/
relocatable link/int81 inspection. No selected startup/native acceptance. Sys-init
0199 consumed session/redirection on host. Next linked shell/one greeting consumer,
authenticated binding/history/factory/copy/immutable exec/parent preservation,
complete fit and matched native dispatcher/readiness/shutdown witness. Full ULs open.

Authoritative work list. Statuses: ready, active, waiting, done, later. Waiting
means a named prerequisite is absent; reassess against current evidence, not a
milestone label. Each completion records commands/results in STATE or linked
experiment evidence and creates follow-ons for unresolved scope.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-001 | done | Establish intent, ownership, sourced preliminary research and milestone tracking | Evidence: initial documents and source manifest |
| UL-002 | done | Pin musl release/source; audit startup, TLS, syscall, memory, signals, fork and threading paths; compare native port vs Linux-interface adapter, patch burden and authority mapping; record recommendation and unresolved APIs | Evidence: docs/research/MUSL-1.2.6-AUDIT.md; implementation follow-ons UL-014/015/016 |
| UL-003 | active | Specify smallest C/musl consumer ABI: image, initial stack/auxv, TLS, FP/SIMD, memory, FDs, exit/error behavior; agree implementation owners and negative tests | Consumer handoff: docs/NATIVE-C-HANDOFF.md; host model UL-020 and bounded native-c experiment; broader service/ABI acceptance remains open |
| UL-004a | done | Compile integer-only freestanding C to inspected x86-64 ELF relocatable object on host | experiments/c-object/README.md; no link/runtime claim |
| UL-004b | done | Inventory/install or locate suitable LLVM SDK; pin versions; compile and link isolated ELF, inspect segments/symbols/runtime dependencies; prove missing target libraries cannot fall back to host | Linux reference SDK passes with compiler-rt arithmetic witness; production Aether ABI remains UL-003 |
| UL-005 | done | Draft SDK/package handoff with build/host/target identity, source and patch hashes, sysroot dependencies, modes/links, static-library rebuild tracking; exercise private staging in owning package project when supported | Maintainer-approved bounded SDK handoff and local preflight; docs/evidence/sdk-review-2026-09-07/README.md. UL-078/079 retain supported package updates and denial native reclaim; UL-003/016/012 broader gates unchanged |
| UL-006 | done | Implement and run minimal static musl C suite: startup/TLS/BSS, allocation failure, bounded I/O and exit; malformed input and denied capability tests | M2 accepted for bounded native profile: UL-033 twelve-case suite; broader services/ABI remain UL-003/007/008/015 |
| UL-007 | active | Port/test dash and process/FD semantics; command substitution, pipelines, redirection, wait, failed exec, pipe EOF and child cleanup | Private scripted SESSION-01–06 independently qualified across910 native cases; experiments/dash-native/SESSION-ACCEPTANCE.md. RECOVERY-01–06 independently accepted (133 native cases); EXEC-SESSION-01–06 also accepted (142 native cases); SCRATCH-SESSION-01–06 accepted (154 native cases); SERIAL-SESSION-01–06 accepted (169 native cases); UL-081 assessment complete; userland-owned runtime extraction/candidate passes49 fresh native executions; next independent technical/reader review and SSDK disposition; full M3/R1 remain open |
| UL-008 | waiting | Serial TTY contract and tests: raw/canonical modes, signals, session/groups, foreground access, disconnect, terminal restore | Draft requirements any time; native tests need UL-007 and TTY service |
| UL-009 | waiting | Pin/build ncurses terminal support and Zsh; selected built-in modules, reviewed startup/completion paths; editing, jobs and UTF-8 behavior tests | UL-007/008; package versions and patches reviewed |
| UL-010 | active | Research UID/GID-to-capability mapping, authorized login/recovery, entropy/password prerequisites, grant inheritance and service ownership; specify abuse/failure tests | [Principal/session review proposal](../docs/quality/IDENTITY-REVIEW.md) ready: two principals, target-scoped test-service restart, inheritance/revocation/cleanup questions. Owner decisions and verifier prerequisites pending; LI-01–10 NOT RUN; post-R1 scope |
| UL-011 | active | Compare selected Toybox/GNU/BusyBox utilities against actual shell/package scripts; maintenance, licenses, portability, deps and upstream tests; produce command/provider matrix | Host research independent; uutils deferred until Rust std target feasibility |
| UL-012 | waiting | Boot exact staged package set under sys-init policy; verify incompatible/corrupt artifacts, missing service dependency, shell failure and authorized recovery | UL-005/009/010/011 plus companion target support |
| UL-013 | active | Apply Distribution PX-01 POSIX.1-2024 reference; define subset and test strategy; separate shell utility coverage from full OS conformance; establish size/startup/RSS workload protocol | Initial inventory/test plan UL-031 complete; TR-B01/02 byte subset and10 two-provider tests now recorded (docs/compatibility/TR-BYTE-SUBSET.md); TRI-01–07 owner handoff prepared (docs/TR-OWNER-HANDOFF.md), all owner cases NOT RUN; first TR-B01 workload protocol plus7 correct Linux/QEMU runs recorded (docs/evidence/tr-workload-2026-09-07/README.md); wider clauses,resource/native workloads and performance targets remain |
| UL-014 | done | Build pinned Clang/musl reference; inspect linked symbols/disassembly and runtime traces for startup/I/O/exit and allocator variants; capture exact call set and toolchain inputs | Built/inspected and 8 QEMU Linux cases pass; traces in experiments/musl-reference/RUNTIME.md |
| UL-015 | active | Prototype native transport retaining musl internal conventions; audit all assembly entry paths, bound buffers and deny unauthorized calls; compare patch delta with reference | Bounded native transport implemented in native-c; all-path audit and broader support await UL-003; decision 002 |
| UL-016 | ready | Independently verify source signature/key policy and review post-release fixes before release packaging; record trust decision and outstanding advisories | pkg-mgr coordination; current pin sufficient only for source research |
| UL-017 | done | Supply pinned Linux x86-64 compiler-rt builtins, verify architecture/dependencies and 128-bit division witness; reject host runtime fallback | 173 x86-64 members; signed/unsigned arithmetic passes; missing-runtime link fails; scope in RUNTIME.md |
| UL-018 | done | Establish isolated Linux x86-64 reference execution/tracing; run startup/allocator probes with positive and negative inputs; save kernel/emulator/tracer identity and syscall traces | Reused running Podman VM; pinned local tool image, QEMU 10.0.11 guest traces; temporary setup container removed |
| UL-019 | done | Extend bounded reference coverage for allocator exhaustion/fallback, large TLS, short/interrupted output and protection failures; separate emulated and native guarantees | 18 cases across UL-021/023/024/025/026/027; RUNTIME.md matrix records injection and limits; native acceptance remains UL-003/006/015 |
| UL-020 | done | Validate bounded static ELF and construct initial-stack model from pinned musl reference binaries; reject malformed image/startup inputs; publish concrete companion handoff | Two real images and 46 rejection cases pass; host-only model, not native launch or adapter |
| UL-021 | done | Exercise large initial TLS allocation, initializer/zero-fill/alignment and mutation checks; corrupt ELF initializer must fail before success output | Three QEMU Linux cases pass; experiments/musl-reference/large-tls-evidence.json; native profile unchanged; remaining UL-019 cases stay ready |

| UL-022 | done | Inspect canonical standards, verify all three offline releases/pins, require applicable profiles in agent guidance, map local work and reconcile stale runtime status | docs/STANDARDS.md; docs/DISTRIBUTION.md; docs/research/STANDARDS-REVIEW.json; documentation/integrity scope only |

| UL-023 | done | Exercise bounded allocation failure, realloc preservation, calloc overflow, release/reallocation and larger-limit negative control | Two QEMU Linux cases pass; experiments/musl-reference/allocator-failure-evidence.json; host limit includes emulator; remaining UL-019 scope stays ready |

| UL-024 | done | Exercise short pipe output, EINTR without copied bytes, exact explicit retry and omitted-retry negative control | Two Linux-emulated cases pass; experiments/musl-reference/interrupted-output-evidence.json; native signals/pipes and broader interruption schedules remain open |

| UL-025 | done | Verify protection errors, restoration, read-only/no-access/unmapped faults with exact address/code, and omitted-protection control | Five Linux-emulated cases pass; experiments/musl-reference/protection-evidence.json; native enforcement and broader memory cases remain open |

| UL-026 | done | Inject internal remap ENOSYS; verify successful realloc allocation/copy/free fallback and real-remap/corrupted-copy controls | Three Linux-emulated cases pass; experiments/musl-reference/allocator-fallback-evidence.json; injection is not native enforcement; metadata/brk exhaustion remains UL-019 |

| UL-027 | done | Block brk growth; verify metadata mmap/mprotect fallback, one injected metadata ENOMEM with successful retry and no-guard control | Three Linux-emulated cases pass; experiments/musl-reference/allocator-metadata-evidence.json; pool-wide/native exhaustion not claimed |

| UL-028 | done | Turn bounded reference evidence into canonical shared native-memory draft and local implementation/acceptance plan | Aether-standards/docs/NATIVE-C-MEMORY.md; docs/NATIVE-MEMORY-PLAN.md; proposal only; owner agreement UL-003 and native implementation UL-006/015 remain open |

| UL-029 | done | Exercise first-query raw brk ENOSYS and metadata protection EACCES/ENOSYS; compare strict error patch with baseline | Four Linux-emulated replacement-object cases pass; RUNTIME.md and adapter-errors-evidence.json; native patch/entry tests and owner agreement remain UL-003/006/015 |

| UL-030 | done | Adopt strict metadata-protection condition in native musl build, record patch/archive hashes and run scoped native descriptor regressions | Four target outcomes pass; docs/evidence/strict-native-libc-2026-09-05/summary.json; allocator branch execution still requires UL-006 mechanisms |

| UL-031 | done | Publish initial POSIX.1-2024 consumer inventory with native status/evidence and planned shell acceptance cases | docs/compatibility/README.md; 28 interface families, 10 planned shell cases; no conformance/runtime promotion; broader UL-013 remains active |

| UL-032 | done | Adopt kernel native-memory v1 in userland libc adapter and combine allocator/protection tests with descriptor and supervised generations | docs/NATIVE-MEMORY.md; nine target cases and four fresh descriptor regressions pass; broader M2/ABI/POSIX acceptance remains open |

| UL-033 | done | Review original M2 gates; add combined startup and malformed-artifact checks; retain exact native acceptance scope | Twelve native cases pass; docs/M2-ACCEPTANCE.md; M2/UL-006 closed only for bounded profile |
| UL-034 | done | Pin/build dash Linux-reference candidate with Clang/musl, review configuration/dependencies and identify concrete script process/FD/file requirements | Pinned dash 0.5.13.5 + Clang/musl build and twelve Linux-reference outcomes pass; docs/research/DASH-0.5.13.5.md; native UL-007 and release-trust UL-016 remain open |

| UL-035 | done | Audit musl process/FD paths and build a bounded process/descriptor reference witness: fork memory, shared offsets, CLOEXEC, failed exec, status/reap and pipe failure cleanup | Nine Linux-reference outcomes pass; docs/research/MUSL-PROCESS-FD.md; native ownership/support and masking/close assumptions remain UL-003/007/015 |

| UL-036 | done | Exercise musl F_DUPFD_CLOEXEC and pipe2 fallback setter failures; retain explicit injection, detect leaked flags/FDs and evaluate checked adaptation | Twenty replacement-object Linux outcomes pass; experiments/descriptor-fallback/README.md; checked patch remains experimental, atomicity/close gates remain open |

| UL-037 | done | Consolidate dash/process/descriptor findings and witnesses into a canonical shared native process/FD draft, with bounded initial workload, ownership questions, atomicity and signal-mask/close gates | Canonical Distribution v0.2.0 draft PROCESS-FD.md PD-01–12; pending four-owner review, no approvals; docs/NATIVE-PROCESS-PLAN.md; releases/pins unchanged |

| UL-038 | done | Build an independent userland consumer of existing bounded executable-launch/channel profiles; verify copied args, ordered data, EOF/EPIPE, endpoint transfer denial/rollback and cleanup/reuse | Six native cases pass; experiments/native-channel/README.md; independent C adapter/helpers, owner kernel conformance supervisor; no sys-init/POSIX/M3 promotion |

| UL-039 | done | Inspect current read-only file-service/two-endpoint producer contracts and build an independent userland client with protocol, authority, malformed input, data and cleanup controls | Four native cases pass; experiments/native-files/README.md; independent client/startup bridge with owner Rust service; read-only scope, no VFS/sys-init adoption |

| UL-040 | done | Independently evaluate optional writable scratch service: write-root separation, failed-create rollback, capacity/overflow, read-only aliases, sparse zero fill and truncate/extend clearing | Four writable native cases plus four fresh read-only regressions pass; experiments/native-files/WRITABLE.md; no POSIX shared offsets/persistence/sys-init adoption |

| UL-041 | done | Prototype/test a bounded single-client userland descriptor layer over the native file protocol: local tables, duplicate shared offsets, close/refcounts and error cleanup | Four native descriptor outcomes and eight file-client regressions; experiments/native-files/DESCRIPTORS.md; four FDs/two open records, no libc interposition or fork/exec inheritance |
| UL-042 | done | Inject descriptor transport/reply and final-close failures; verify poisoned connection, no replay, local publication and dup2 reference cleanup | Seven native fault-handling/control outcomes plus twelve regressions; experiments/native-files/FAILURES.md; reply-field validation fixed, no replay/reconnection/libc claim |
| UL-043 | done | Audit and build a bounded libc file adapter witness using the tested descriptor layer; exercise real C entry points, errno and unsupported operations | Four libc native cases plus nineteen regressions; experiments/native-files/LIBC.md; musl read/write/close/dup/dup2 and adapted public open/lseek, no stdio/process/TTY claim |
| UL-044 | done | Audit and test bounded musl buffered-file entry points, internal seek/vector I/O, flush/errors and cleanup over the file facade | Four native FILE cases plus twenty-three regressions; experiments/native-files/STDIO.md; input fflush error/data preservation and raw-hook errno fixed, no full stdio or shell claim |
| UL-045 | done | Refresh native dash integration gaps against current companions and bounded libc/FILE results; prepare the next executable workload and mechanism handoff | Current broker/lookup/ABI-6 inputs and dash source compared; docs/NATIVE-DASH-GAPS.md; three requester ELFs prepared, no native execution or PD acceptance |
| UL-046 | done | Execute independent broker requester against captured owner broker/worker; test namespace, empty inheritance, collection and partial/exit cleanup with owner controls | Six native broker outcomes pass; experiments/native-process/RUNTIME.md; receipt-matched source restoration, independent policy/cleanup controls, no POSIX process/inheritance claim |
| UL-047 | done | Independently consume the completed ABI 7 broker/file coexistence profile | Six native cases plus six ABI 5 regressions pass; experiments/native-process/COEXIST.md; pinned producer archive, rejected-frame alignment, ticket isolation, file data and cleanup; no inherited FD or shell claim |
| UL-048 | done | Publish proposed UP-01/UP-02 integration follow-ons to Aether roadmap | User explicitly authorized exact UP-01/UP-02 entries; appended to Aether .planning/ROADMAP.md, links verified and earlier roadmap preserved; docs/AETHER-BACKLOG-FOLLOWONS.md |

| UL-049 | done | Review ABI 8/9 capacity and independently consume the completed multi-client connection profile | Six ABI 9 native cases pass with both clients independently rebuilt; experiments/native-process/CONNECTIONS.md; ABI 8 program-stop workload reviewed only, no general inheritance or shell claim |

| UL-050 | done | Independently consume fixed-alias shared-files bootstrap, narrowed rights, shared position, both exit orders and final close | Six native cases pass; experiments/native-process/SHARED.md; independent clients and exact owner controls; no libc interposition, general inheritance or shell claim |

| UL-051 | done | Independently consume parent-requested one-entry admission, rollback and consuming child-result collection | Nine native cases pass against completed collection snapshot; experiments/native-process/INHERITED.md; independent clients, both exit orders, exact failure controls; no general POSIX/shell claim |

| UL-052 | done | Review broker-owned references/positions against local libc/FD facade and specify bounded integration | docs/INHERITED-LIBC-PLAN.md; source-pinned review identifies conflicting local offsets, hook linkage, fixed indices/counts and close/result ownership; no new runtime claim |

| UL-053 | done | Implement bounded inherited musl read/close with independent probe and admission/collection controls | Fourteen native cases pass; experiments/native-process/INHERITED-LIBC.md; real musl entry points, errno, unsupported counts, consuming close, whole-connection poison/no replay; no general read/EOF or shell claim |

| UL-054 | done | Review delivered general-size file-I/O owner extension and select the libc workload | docs/GENERAL-FILE-IO-REVIEW.md; completed separate file-io mode already supplies bounded reads/EOF/writes; no redundant sibling request or standard change |

| UL-055 | done | Independently consume file-io with real musl reads/writes/close, short results, EOF, capacity and uncertain-reply controls | Ten final native cases pass; experiments/native-process/FILEIO-LIBC.md; zero operations validate owner state, full storage readback; no general command/shell claim |
| UL-056 | done | Review CR-01/command-I/O candidate and prepare real bytecount source, controls and native object | Ten host-libc and eleven injected controls pass; experiments/command-runner/README.md; docs/COMMAND-IO-REVIEW.md records two-binding/startup and verifier boundaries; no native command execution |

| UL-057 | done | Independently execute finite runner/bytecount with two-binding command protocol | Nine native cases pass; experiments/command-runner/NATIVE.md; independent adapter/runner and unchanged bytecount; public runner/full CR-01 remain open |

| UL-058 | active | Exercise command bootstrap, malformed frames and unknown reply boundaries | Scoped CB-01–14 and NB-01–04 witnesses recorded; latest 30 combined native, nine original-pin and 21 host regressions pass (docs/evidence/native-terminal-userland-2026-09-06/summary.json). Independent reviews, public startup outcome coverage beyond the scoped UL-059 observer, wider race/stop/unknown recovery and ASan (UL-062) remain open; no full process acceptance |
| UL-059 | active | Specify and independently adopt public aether-run startup/status mapping | docs/RUNNER-INTEGRATION.md selects verified AERUN001/combined producer input; NB-01–04 scoped native witnesses now pass. Pure decoder/selector now passes 1293 UBSan assertions, two semantic mutants and native object inspection (docs/evidence/runner-parser-2026-09-06/summary.json). Opt-in native carrier and independent full argv/env observer now pass three positive cases and one semantic rejection (docs/evidence/runner-startup-2026-09-06/summary.json); all34 combined/nine legacy pass, prior25 ELFs identical. Pure result decoder/policy now passes 28,159 UBSan assertions, four semantic mutants and native object inspection (docs/evidence/runner-results-2026-09-06/summary.json). Native mapping now passes ten positives and three exact controls; all47 combined/nine legacy pass, prior28 ELFs identical (docs/evidence/runner-mapped-2026-09-06/summary.json). docs/RUNNER-LOCAL-OUTCOMES.md now supplies proposed RL-01–12 and exact local-output fixtures; owner review/adoption pending, no sibling change. Mapped-path host controls now pass25 scenarios/four semantic mutants (docs/evidence/runner-uncertainty-2026-09-06/summary.json), production unchanged. Six native mapped uncertainty controls now pass; all53 combined/nine legacy pass and prior42 ELFs match (docs/evidence/runner-native-uncertainty-2026-09-06/summary.json). Nine native startup rejection/publication controls now pass; all62 combined/nine legacy pass, prior48 ELFs identical (docs/evidence/runner-native-startup-2026-09-06/summary.json). Superseded witness-pointer defect attempt retained; corrected full rerun passed. Four native pending-budget controls now pass; all66 combined/nine legacy pass and prior57 ELFs match (docs/evidence/runner-native-budget-2026-09-06/summary.json). Native control-flow uses local pending/yield injection, not remote timeout evidence. Host local-output delivery now passes6130 UBSan scenarios/four semantic mutants (docs/evidence/runner-local-delivery-2026-09-06/summary.json); single-use callback candidate only, no native wiring. Host frontend integration now passes280 UBSan scenarios/three mutants (docs/evidence/runner-local-frontend-2026-09-06/summary.json); actual parser/admission decoder selects pinned text, no native wiring. Consolidated docs/RUNNER-OWNER-HANDOFF.md is ready, not sent; 6956 retained evidence files verified and four current owner inputs match. Waiting for owner-reviewed native output-role/lifecycle contract and immutable producer bundle; native RL outcomes and independent review remain open. Local UL-067 can proceed; UL-069 deferred. Zero-admission/help/error/recovery and package/sys-init acceptance remain open; default legacy pin unchanged |

| UL-060 | done | Review approved standards drafts and adopt local development process with pinned inputs and offline gate | docs/quality/PROCESS.md; coverage starts draft, release gate rejects incomplete coverage; no runtime or blanket compliance claim |
| UL-061 | ready | Complete documentation/public-surface and stable test-case inventory, exact source identities and independent reader review | DP/TC; expand initial subsystem inventory and add manuals/target lookup before shipment |
| UL-062 | active | Implement bounded extended workloads, sanitizer/static coverage and stage/family metrics | Extended matrix and native compensation limits pass on Python 3.10.21/3.14.7 (docs/evidence/extended-matrix-2026-09-07/README.md). PXE-04 blocked, no waiver. Remaining: compatible ASan toolchain/OS, kernel RSS, broader corpora/schedules, independent review; weekly suite NOT RUN |
| UL-063 | active | Audit/migrate existing first-party coding practices, starting with command-runner | docs/quality/COMMAND-RUNNER-REVIEW.md; six C/header files formatted, five native ELFs identical, 21 host/control cases pass; CSR-01/02 corrected: seven process/environment checks, hostile-env build, 21 host/control and nine native cases pass; docs/evidence/command-tooling-2026-09-06/summary.json; CSR-03 C17/stale-scenario migration passes 21 host/control and nine native cases, five ELFs identical (docs/evidence/command-c17-2026-09-06/summary.json); CSR-03 entry-point/named-source restructuring passes 21 host/control, seven process and nine native cases with matching argv/exits and five ELF bytes (docs/evidence/command-readability-2026-09-06/summary.json); independent reviews and broader migration remain |

| UL-064 | done | Produce initial command/provider matrix from pinned dash builtins, current upstream status and actual package-script needs | docs/research/BASE-PROGRAMS.md; 39 requirement groups, research only; UL-011 remains active |
| UL-065 | done | Pin/audit minimal Toybox source/config/closure; build with Clang/musl and exercise upstream plus independent reference cases | experiments/toybox-reference/README.md; 22 independent cases, 162 upstream cases, two helper controls; native follow-on UL-067 and trust UL-016 remain open |
| UL-066 | active | Compare pinned awk providers against package scripts; review tr/stty alternatives and dependency/maintenance/security costs | 33 host cases pass across pinned One True Awk/mawk/gawk; experiments/awk-reference/README.md; mawk static musl passes 50 upstream groups, FPE suite and 11 consumers after verified macro detection; GNU/BusyBox source comparison pinned; UL-068 headers complete; GNU static tr/stty passes 17 Linux-QEMU cases; BusyBox minimal static build passes ELF inspection, matches 13/17 common fixtures (four tr differences), and passes 5 focused upstream tests; fresh GNU remains 17/17; docs/evidence/busybox-tr-stty-2026-09-06/summary.json; GNU tr.pl passes 134 cases plus rejection control; docs/evidence/gnu-tr-upstream-2026-09-06/summary.json; tr shell C-locale cases and 11 stty row/column checks pass with exact PTY restoration; no-TTY control skips 77; docs/evidence/gnu-shell-2026-09-06/summary.json; static getlimits plus stty-invalid passes 2 overflow/4 device-argument/12 speed rejections with restoration; docs/evidence/gnu-stty-invalid-2026-09-06/summary.json; extended main returns 0 but fails independent restoration; pairs completes with 188 cmspar failures; CMSPAR translation omission corrected by UL-069 with full isolated builds and12 direct PTY cases; corrected-emulator GNU pairs now passes with restoration; main-script restoration still fails; common GNU17/17 and BusyBox13/17 unchanged; docs/evidence/qemu-consumer-regression-2026-09-07/README.md; docs/evidence/gnu-stty-extended-2026-09-06/summary.json; all5 legacy BusyBox scripts exit0 and5 failure controls reject; supplementary ROT13 assumption resolved by8 GNU/BusyBox byte comparisons: ordinary brackets literal, no new provider defect (docs/evidence/tr-ranges-2026-09-07/README.md); historical failed expectation preserved; static speed-error boundary now passes3 private link-time PTY cases, baseline ELF identical (docs/evidence/stty-speed-2026-09-07/README.md); upstream LD_PRELOAD script remains NOT RUN; 10 locale observations show ISO-named musl locale uses UTF-8, so ISO branch remains unsupported/NOT RUN (docs/evidence/candidate-locale-2026-09-07/README.md); bounded provider packet reviewed (docs/quality/PROVIDER-REVIEW.md);10 UTF-8 characterization cases demonstrate byte semantics and unmet character expectations (docs/evidence/tr-utf8-2026-09-07/README.md); 5 archives/16 current sources/9 evidence identities verified; source/security/independent review remain |

| UL-067 | active | Audit minimal Toybox linked/startup paths against native APIs; evaluate standalone cat/wc before target port | UL-065 reference result; pinned-source/import/ELF audit recorded in docs/research/TOYBOX-NATIVE-AUDIT.md and docs/evidence/toybox-native-audit-2026-09-06/summary.json. Standalone keeps shared startup; filename close and flush/exit gaps identified; later reference witnesses follow. Standalone cat/wc now pass 10 independent/34 upstream cases and two oracle controls; 79,888/85,848-byte ELFs with shared startup retained (docs/evidence/toybox-standalone-2026-09-06/summary.json). Direct I/O fault slice passes seven reference cases/two oracle controls/six host UBSan controls (docs/evidence/toybox-io-faults-2026-09-06/summary.json): short I/O completes, EINTR fails, close EIO ignored. Locale/buffered slice passes eight reference cases/two oracle controls/four host UBSan controls (docs/evidence/toybox-locale-buffered-2026-09-06/summary.json). docs/TOYBOX-NATIVE-CAT.md proposes stdin-only scope, startup/finalization and CAT-01–08 (all native NOT RUN). docs/research/TOYBOX-NATIVE-SDK.md verifies231 SDK files/18 musl sources; built-in locales, unsupported umask/writev and candidate _xexit seam recorded. Host finalizer passes2,560 scenarios/six invalid controls/three mutants (docs/evidence/toybox-finalizer-2026-09-06/summary.json), no native wiring. Private vector candidate passes36,992 host scenarios/eight controls/three mutants (docs/evidence/toybox-vector-2026-09-06/summary.json); VECTOR.md records libc integration and unimplemented mask state. Actual musl write-loop reference passes9,720 cases/pipe control/two mutants (docs/evidence/toybox-stdio-loop-2026-09-06/summary.json), with failed attempts retained. Shared host session passes4,096 scenarios/four controls/three mutants (docs/evidence/toybox-session-2026-09-06/summary.json), no native wiring. Host mask state passes1,048,576 scenarios/three mutants (docs/evidence/toybox-mask-2026-09-06/summary.json); no native umask. Combined Toybox fixture passes eight Linux cases/wrong-mask mutant/oracle controls (docs/evidence/toybox-composed-2026-09-06/summary.json); control ELF identical. docs/TOYBOX-OWNER-HANDOFF.md recorded in Aether UP-02/STATE at user request; waiting for reviewed cat admission/child diagnostic/lifecycle bundle before native adaptation; umask/locale/metadata/TTY and identity/grants remain owner contracts |
| UL-068 | done | Add pinned Linux UAPI headers in a separate reference SDK view; preserve musl baseline and verify headers/tool generation/ABI provenance | experiments/linux-uapi/README.md; 1028 headers, full extraction verification, four rejections, unchanged musl baseline; GNU tr/stty build and 17 Linux-QEMU cases pass; UL-066/008/012/016 remain |
| UL-069 | done | Correct or replace the isolated Linux reference emulator's CMSPAR translation with pinned source/patch provenance | UL-066 diagnosis; approved guarded CMSPAR patch, full pinned offline original/patched builds and12 direct PTY/restoration cases pass (docs/evidence/qemu-offline-build-2026-09-07/README.md). All103 installed package versions match pins. Build/runtime slice approved. Consumer rerun clears all188 CMSPAR pair failures with restoration; main-script natural restoration still fails; GNU17/17 and BusyBox13/17 unchanged (docs/evidence/qemu-consumer-regression-2026-09-07/README.md). Consumer adapters approved; explicit recovery now passes after main script, exit23 and timeout, with omitted-recovery rejection and final rescue (docs/evidence/qemu-recovery-2026-09-07/README.md). Natural main-script restoration remains false. Recovery approved; bounded emulator correction closed. UL-066 retains natural main-script cleanup, locale/static-fault/provider gaps; UL-008 native terminals and UL-016 source trust remain; preserve image and prior failures; no native TTY acceptance |

## Decision questions

- Q1 / UL-002: Can a narrowly scoped Linux-interface adapter preserve capability
  authority with less maintenance than a musl native port? Native transport preserving internal conventions is selected for experiment (decision 002); no system ABI accepted.
- Q2 / UL-003: Who owns each POSIX runtime service and its mutable state? What
  initial ABI is sufficient for a real musl program rather than a libc-free fixture?
- Q3 / UL-007: How will fork, signals and descriptor inheritance be supported?
  A launch-only replacement must prove any required shell modifications.
- Q4 / UL-010: How are operator authentication and administrative grants represented?
  UID 0 alone cannot grant universal native rights.
- Q5 / UL-005/012: Which target file metadata and startup artifacts can pkg-mgr
  preserve, and which service descriptors will sys-init actually consume?
- Q6 / UL-011/013: Which utilities and POSIX behavior constitute the first supported
  base, and how will release/security-fix maintenance be staffed and measured?

Suggested execution order: UL-058 exercises the new command integration failure boundaries while the PD shared draft remains pending owner review; accepted broader work then extends UL-003 ownership/contracts and UL-015 transport. UL-006/M2 and UL-019 are complete within their bounded profiles; UL-016 remains the release trust gate.
Use UL-005/010/011/013 for independent progress when native implementation waits.

## Native startup witness, 2026-09-05

UL-003/015 now have a bounded native experiment and UL-006 startup/context/I/O/exit
coverage under [native-c](../experiments/native-c/README.md). Their broader ABI,
allocator, service-owned transport and production prerequisites remain open; no
whole-story completion is inferred. UL-007/008 retain process/FD/TTY dependencies.


## Coordination update

The user reports Aether's prerequisite work complete and authorizes resumed
integration. Native-memory v1 is now implemented by Aether and adopted in the
bounded userland fixture (UL-032). The previous hold is lifted. No permission to
replace unrelated sibling implementations or background monitor is inferred.

## RC1 standards review follow-up

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-070 | done | Review unpublished RC1 and ADP-02; record exact clauses, compatibility, coverage, exceptions and gaps; run documentation checks and commit review | docs/quality/RC1-ADP02.md; docs/evidence/rc1-adp02-2026-09-06/README.md; 116 clauses, unchanged pins, local/candidate checks pass and release preflight correctly blocks; independent review and runtime acceptance remain separate |

ADP-02 extends the existing migration work without resetting its status:

- UL-060: initial adoption remains complete; RC1 contains identical approved snapshot bytes.
- UL-061: complete exact-revision public/interface/test inventory, mdoc manuals, renderer/tool identities, packaged offline lookup, independent technical and onboarding/recovery reader reviews.
- UL-062: supply bounded fuzz/stress/concurrency workloads, fixed corpora, sanitizer/static scope, duration/resource metrics and fresh candidate evidence; retain missing minimum-interpreter execution.
- UL-063: finish broader C and generated/imported Rust/FFI audits, declared Python/shell/make tool scope, selected CERT topic mapping and scoped suppression register; preserve upstream/generated/historical bytes.

No release exceptions approved. UL-059/067 remain waiting on native producer
contracts/bundles. Post-R1 architecture is outside this review.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-071 | active | Write the actual quality 0.1.0 host command manual, bind source/options/cases in inventory, exercise CLI and lint/terminal/HTML outputs | docs/evidence/quality-manual-2026-09-06/README.md; UL-061 slice only; independent reader/technical review, browser visual check and packaged lookup remain open |

UL-063 follow-up from manual control-flow review: migrate docs/quality/check.py
and its release-check wrappers to an explicitly owned process-tree strategy before
claiming bounded descendant cleanup. Current direct-child timeouts are documented,
not a global watchdog. Keep pin verification ahead of copied checker execution and
preserve exit 0/1/64 and output markers in any separately tested behavior change.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-072 | done | Own quality/reference process sessions, bound output/deadlines, retain cleanup and preserve CLI contracts | Implementation and host controls in docs/evidence/quality-process-2026-09-06/README.md; Python 3.14/3.13 and CLI/manual regressions pass; UL-073 qualifies 3.10.21/3.12.14; maintainer approved the packet with no findings (source-inventory-2026-09-06/maintainer-review.json); broader UL-063 remains open |

The quality-wrapper process ownership implementation described in the earlier
UL-063 follow-up is now in UL-072. Do not treat the original direct-child limitation
as current implemented behavior; keep its historical evidence unchanged.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-073 | done | Provision isolated pinned Python 3.10/3.12 series runtimes, execute quality-path qualification and prepare manual review handoff | docs/evidence/python-qualification-2026-09-06/README.md; 12 invocations per runtime pass on 3.10.21/3.12.14; limited offline builds, not full Python distributions; docs/quality/MANUAL-REVIEW.md prepared for the user; actual sign-off remains pending |

UL-072's missing-runtime prerequisite is now satisfied for the quality paths on
the exact tested minor-series patch releases. Independent technical review remains
pending; the user will perform it manually. UL-071 still requires visual/reader
review and packaged lookup. Broader UL-061–063 scope and native producer dependencies
are not closed by these tests.

## Maintainer acceptance and source census — 2026-09-06

The maintainer has now approved the review packet with no findings. This supersedes
pending sign-off above for UL-072 and the presented UL-071 packet; no detailed
reviewer execution/visual logs were supplied. Packaged lookup remains open, so
UL-071 stays active. This is not approval of the new census or all source audits.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-074 | done | Snapshot 180 maintained source/patch paths, exact hashes, languages and documentation routes; reject six altered-record controls and compare independent filesystem census | docs/evidence/source-inventory-2026-09-06/README.md; static discovery only; UL-061 surface/manual inventory, UL-062 workloads and UL-063 audits remain open |

Next local slice: review Python subprocess boundaries using source-inventory.json
as a discovery index, beginning with host experiment entry points. Existing scoped
quality and command-runner evidence is preserved; aliases/generated calls still
require source inspection. Native UL-059/067 continue to require producer bundles.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-075 | done | Harden dash import inspection: explicit pin/empty checks, owned nm session, explicit cwd/environment and bounded output/wait | Scoped implementation and host/Linux qualification evidence accepted by maintainer on 2026-09-07; docs/evidence/dash-review-2026-09-07/README.md |

UL-075 remaining local follow-on: audit dash build.py and test.py lifecycle,
including remote container cleanup, before claiming bounded execution there.
The UL-074 dated source census is superseded for the changed import auditor and
new test by UL-075 sources.json; existing historical hashes remain intact.

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-076 | done | Own dash test-helper compiler process session, environment/cwd, wait/output limits and cleanup receipt | Scoped implementation and host/Linux qualification evidence accepted by maintainer on 2026-09-07; docs/evidence/dash-review-2026-09-07/README.md |
| UL-077 | done | Establish remote container lifecycle ownership for dash target generators and guest tests | Scoped implementation and host/Linux qualification evidence accepted by maintainer on 2026-09-07; docs/evidence/dash-review-2026-09-07/README.md |

UL-076 does not close the remote process gaps found in UL-075's follow-on audit.
Retain the UL-074 historical census; UL-076 sources.json identifies changed test.py
and new host-build.py/test-host-build.py under the dash-reference documentation route.

UL-077 is now active: container-process.py prototypes explicit create/start/remove
with pinned client and fixed connection, ownership inspection and absence queries.
Eleven modeled outcomes pass on Python 3.10.21/3.14.7. Three real existing-VM controls
pass; the timeout witness observes a still-running remote container after local
client termination, then exact-ID removal and name/ID absence. Evidence:
docs/evidence/dash-container-2026-09-06/README.md.

Remaining UL-077: integrate read-only test mounts and writable generator mounts,
keep guest semantics/markers, run full dash regression and affected build controls,
obtain independent review and exercise true remote service/creation ambiguity.
The prototype does not yet replace either launcher's existing remote path.

UL-077 guest-test integration now passes: both Python 3.10.21 and 3.14.7 run all
twelve cases with unchanged scripts/exits/stdout and exact dash/helper bytes.
Independent queries confirm all 24 containers absent by name and ID. Evidence:
docs/evidence/dash-container-integration-2026-09-06/README.md.
This supplies UL-076's full guest integration witness; its independent review remains
pending. UL-077 next implements writable target generators and runs affected builds;
review/live ambiguity gates remain open. Current release pins are unchanged.

UL-077 writable generator integration now passes. The top-level builder owns all
four target generator lifecycles outside local make's timed process tree; compile
wrappers exec, and four fail guards prevent unplanned make execution. Input/output
and guard stability checks pass on the final Python 3.10.21 build. Live parent-write
denial, identical reference ELF, 99 imports, twelve fresh guest cases and 42 independent
absence queries pass. Evidence: docs/evidence/dash-generator-2026-09-06/README.md.

Remaining UL-077: independent technical review and true remote service-loss/creation
ambiguity controls. Build/test integration is no longer pending. Preserve the recorded
metadata-only correction to the old host-sandbox label; no host confinement claim.

UL-077 post-create transport-loss control passes on Python 3.14.7 through a real
loopback relay: actual connection refusal leaves cleanup unresolved, then separate
owned recovery verifies absence. Evidence: docs/evidence/dash-transport-loss-2026-09-06/README.md.
Python 3.10.21 qualification failed before creation because the original endpoint
became unavailable; machine status reports stopped. No VM restart was attempted.
Remaining local fixture work: recovery reporting for no-create/setup failure, then
repeat minimum-version qualification when the VM is available. True in-flight create
response ambiguity and independent review remain open; no broad readiness promotion.

Follow-up in this change: recovery reporting now skips remote calls when no create
request was sent and retains recovery errors instead of masking the original failure.
Three offline controls pass on Python 3.10.21/3.14.7 for no-create, unreachable and
absent cases. The successful earlier live execution is retained as test-executed.py
in the transport evidence packet; final fixture live qualification remains pending
until the existing VM is available. No runtime adapter behavior changed.

UL-077 local relay audit found premature bidirectional closure on one-sided EOF.
Two real loopback controls fail before the fix and pass afterward on Python
3.10.21/3.14.7, preserving response and late-request bytes. Evidence:
docs/evidence/dash-relay-eof-2026-09-06/README.md. Revised relay live qualification
remains pending while the existing VM is stopped; independent review and lost-create
response work remain open. No runtime adapter changes or release acceptance.

2026-09-07: UL-077 revised relay/recovery live qualification now passes on both
Python 3.14.7 and 3.10.21 after user-authorized existing-VM startup. Separate-session
startup left an unavailable endpoint; both setup failures are retained. Keeping
startup, endpoint verification and tests in one execution session passed. Evidence:
docs/evidence/dash-transport-qualified-2026-09-07/README.md. Post-create outage and
owned recovery are qualified; true in-flight/lost-create-response controls and
independent review remain open. No automatic VM monitor or release-pin change.

2026-09-07: UL-077 live in-flight create-response loss now passes on Python
3.14.7/3.10.21. A separate observer witnesses the actual labelled container, the
owned relay cuts queued reply bytes, and the real create client fails without an ID.
The adapter keeps creation unconfirmed and cleanup unresolved; recovery removes only
the witnessed container and verifies absence. Default outage/EOF regressions pass.
Evidence: docs/evidence/dash-create-response-2026-09-07/README.md.

UL-075–077 are ready for independent technical review through docs/quality/DASH-REVIEW.md;
keep them active until actual review is supplied. The planned scoped runtime gates
are no longer missing. Broader UL-061–063 migration and unsupported transport/host
schedules remain separate, not newly asserted completion or release exceptions.

2026-09-07: Maintainer approval closes the scoped UL-075–077 technical review at
commit e01302bc. All 12 reviewed source hashes match. This supersedes the pending
review/integration checkpoints above; historical evidence remains unchanged.
Broader UL-061–063 migration and release/reader/native gates remain open. Next
local work is UL-062 bounded parser workloads and compatible host sanitizers,
with fixed inputs, explicit duration/resource limits and denial/cleanup oracles.

2026-09-07: UL-062 first parser slice adds a fixed 172038-case byte/length sweep,
reserved-byte defect control and signed-overflow instrumentation control. Explicit
UBSan-only qualification is recorded in docs/evidence/parser-extended-2026-09-07.
Combined ASan/UBSan first-control startup timed out both sandboxed and escalated;
retain failed receipts, no silent fallback. ASan, general fuzz/minimization,
transport stress, static analysis, RSS budgets/native compensation and independent
review remain open. This does not close UL-062 or qualify the complete weekly suite.

## UL-062 external implementation handoff — 2026-09-07

The current interrupted slice is **parser failing-input retention, replay and
minimization**, under UL-062. The user reported app security screening and asked
for another service to finish it; the screening trigger is unknown, and no
tool-level rejection was returned. Stop implementation/build work in this task.

Follow [the detailed handoff](../docs/evidence/parser-replay-2026-09-07/README.md)
and its PXR-01–05 plan. Partial edits exist only in parser-extended.c; they are
uncompiled and unvalidated. Complete driver integration, bounded deterministic
reduction, exact-oracle/retention controls and both interpreter qualifications.
Return sources, every attempt's evidence and actual review for local integration.
Keep UL-062 active; the prior ASan startup timeout and wider extended-suite gaps
are separate unresolved items. Do not treat this handoff as a successful build.

2026-09-07: UL-062 parser replay/minimization now passes. Exclusive failure
retention, replay of the reserved-byte defect, original-parser accept, local
minimization, collision/invalid-input controls and synthetic deletion/zero/
non-reproducing/budget oracles are recorded in
docs/evidence/parser-replay-2026-09-07. The first deletion-first reduction
exhausted its 1024-call budget and is retained. ASan, broader exploration,
transport/concurrency stress, static analysis, RSS budgets, native compensation
and independent review remain open. This does not close UL-062.

2026-09-07: UL-062 host static/RSS/concurrency/transport slice now passes.
clang-tidy/analyze silence, null-deref canary, observational 32 MiB RSS budget,
grow/reserve controls, eight forked parser children, 5-second hang cleanup and
256 native_exchange rounds (3072 channel_raw) are recorded in
docs/evidence/extended-host-2026-09-07. Darwin cannot set RLIMIT_AS/DATA. ASan,
broader schedules, native compensation review and independent review remain
open. This does not close UL-062.

2026-09-07: reducer classification no longer treats fixture errors or mismatched
retain files as non-reproduction. Eleven in-process controls and both Python
3.10.21/3.14.7 --ubsan-only suites pass
(docs/evidence/parser-reducer-review-2026-09-07/README.md). UL-062 stays active.

2026-09-07: pinned Clang 21.1.8 ASan deadlocks at shadow-memory init on macOS 27
(AsanInitInternal/LockSlow). UBSan empty main and Apple clang ASan comparison
pass; the Apple compiler is not a pin. PXE-04 remains blocked.
docs/evidence/asan-host-2026-09-07/README.md. UL-062 stays active.

2026-09-07: family/stage matrix and native ASan compensation review pass with
four rejected mutants and no waiver. docs/evidence/extended-matrix-2026-09-07.
UL-062 stays active.

UL-005 consumer preparation: experiments/sdk-consumer now has a verified
pre-import static-link witness plus missing-header/libc failures. Await the real
pkg-mgr export/import result to rerun against imported inputs. Startup/adapters,
compiler helpers, static rebuild and native execution remain separately open.

UL-005 startup review finding (2026-09-07): check-startup.py selects
experiments/native-c/probe.c, while the selected SDK evidence.json probe_sha256
matches io_probe.c. It records current adapter hashes but does not compare them
to the selected receipt before build. Before accepting the planned SDK-05 pinned
startup closure, select io_probe.c and validate probe/I/O/memory source hashes
against that receipt (and receipt identity against libc_receipt_sha256). Add a
changed-source rejection control, rerun affected link cases, retain prior evidence
and correct the scope claim. Current passing evidence remains valid only for its
recorded source set; SDK-07/08 remain open.

2026-09-07: SDK-05 startup correction selects io_probe.c, checks
libc_receipt_sha256 and adapter/probe hashes before compile, and rejects a
mutated io_probe. Rerun pass: docs/evidence/sdk-startup-link-2026-09-07
(sdk-startup-lefmmlgo). Prior probe.c run retained. SDK-07/08 remain.

SDK-05 review correction is resolved: sdk-startup-lefmmlgo sources and 13 complete
process receipts verified. SDK-07 local input/relink witness now passes in
docs/evidence/sdk-static-rebuild-2026-09-07: private archive change invalidates old
input binding; real relink/ELF checks pass despite identical output bytes.
Full package update/reverse-consumer integration and SDK-08 native execution remain
open; no new native acceptance or automatic rebuild system is implied.

2026-09-07: SDK-08 isolated snapshot captured; first QEMU run rejected at
supervisor 214 / native C profile. docs/evidence/sdk-08-native-2026-09-07.
Acceptance remains NOT RUN.

SDK-08 bounded native slice now passes on the retained SDK-receipt-matched
UL-044 producer (docs/evidence/sdk08-matched-2026-09-07). Positive reclaim2 and
exact memory-grant denial are verified; denial native reclaim is not. Previous
NOT RUN checkpoints are historical. Package-owner SDK-07 and independent review
remain before broader UL-005 completion; no full native suite is inferred.

UL-005 acceptance packet ready: docs/quality/SDK-REVIEW.md. SDK-07 owner direct
consumer package-record witness is independently identity-checked locally; this
supersedes the missing-owner-witness checkpoint, not missing supported update
enforcement. Independent review and bounded acceptance disposition remain.
Future supported binding/plan semantics (missing/stale/direct/transitive) belong
to pkg-mgr; denial-native-reclaim is excluded from the current successful claim.

UL-005 / UL-063 copied-source check (2026-09-07): startup harness now verifies
staged probe/adapter hashes before compile. Transient-copy control rejects the
prior implementation and passes the fix; complete link rerun retains identical ELF.
See docs/evidence/sdk-copy-check-2026-09-07/README.md. Private staging ownership
assumption and independent review remain; no new native acceptance claim.

UL-005 / UL-063 receipt-failure retention (2026-09-07): missing SDK/layout files
and malformed SDK JSON now retain incomplete summaries before any process starts.
Three controls, copied-source regression and full startup link pass; ELF unchanged.
Evidence: docs/evidence/sdk-receipt-failures-2026-09-07/README.md. Follow-on: review
parseable receipt schema failures and report-directory creation behavior before
claiming complete preflight failure coverage. Independent review remains pending.

UL-005 / UL-063 consumed-field follow-on (2026-09-07): local object/digest/path
validation now passes 24 invalid-input controls, six libc controls and unknown
metadata acceptance, plus earlier regressions and identical-ELF startup link.
Evidence: docs/evidence/sdk-schema-2026-09-07/README.md. Owner-wide schema policy,
JSON resource/duplicate-key bounds and unavailable report storage remain separate;
independent technical review is still pending.

UL-005 / UL-063 local preflight slice ready for review (2026-09-07): receipt byte/
depth bounds, duplicate/nonfinite rejection and explicit unavailable-storage failure
now pass with previous regressions and unchanged ELF. SDK-REVIEW.md includes the
final source/control inventory and retained nesting-test correction. Review and
bounded acceptance disposition are next; private-filesystem, RSS/total-deadline
and storage-availability limits remain explicit, not implied guarantees.

## SDK acceptance follow-ons — 2026-09-07

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-078 | waiting | Consume supported SDK binding/plan and update integration; reject missing/stale bindings, distinguish direct/transitive consumers, preserve independent candidate pins | pkg-mgr-owned contract/implementation; existing direct-consumer observation is not an update API |
| UL-079 | waiting | Demonstrate native reclaim after denied SDK consumer startup with exact resource inventory and positive/omitted-cleanup controls | Matching owner producer/consumer and a recoverable denial workload; existing reclaimed0 panic does not supply reclaim evidence |

Maintainer approval closes bounded UL-005 and its scoped UL-063 preflight review;
broader UL-063 migration stays active. UL-069 resumes after this handoff checkpoint.

UL-069 resumed after SDK acceptance (2026-09-07): archive and all117 build inputs
verified; guarded CMSPAR row passes extracted host translation checks with original/
wrong-bit rejection and missing-definition controls. Evidence: docs/evidence/
qemu-cmspar-translation-2026-09-07/README.md. Full isolated emulator build and PTY/
GNU/BusyBox tests remain next; no parity waiver or native acceptance.

## Roadmap-first priority and post-release queue — 2026-09-07

Maintainer directs M3 native command/shell delivery ahead of optional refinement.
[Execution focus](../docs/M3-EXECUTION-FOCUS.md) is authoritative for next-work
selection. PRF-01 broader utility/locale corners, PRF-02 extra reference benchmarks
and optimization, and PRF-03 optional providers/polish are deferred until after
release, preserving existing evidence and known limits. They are not release-gate
waivers; defects and checks needed by the chosen native path remain required.

UL-059 is active again: runner-handoff-2026-09-07 is available; all5 artifacts
verify and485 source files are privately extracted with exact hashes/modes.
UL-067 is active for fresh producer review: newer native cat/link/error/usage
evidence exists; independent final handoff compatibility remains to establish.
These updates supersede older waiting descriptions in the historical row detail.
Next: exact native consumer/producer/SDK compatibility, then the real command
flow and dash external command/pipeline. No source/pin/native acceptance inferred
from successful intake. Evidence: docs/evidence/m3-refocus-2026-09-07/intake.json.

UL-059 M3 path checkpoint: new independent four-role parent passes648 host decoder
cases and links against the identical231-file SDK; native NOT RUN. Evidence:
docs/evidence/four-role-consumer-2026-09-07/README.md. Next matched owner/backend/
bytecount boot with actual consumer,output/status/six reclaim and role/close controls.

UL-059 native checkpoint (2026-09-07): the independent four-role command-success
path now passes exact bytecount output/status and six reclaims across two
generations. Wrong-role and omitted-close controls reject as expected. Evidence:
docs/evidence/four-role-native-2026-09-07/README.md. Overall UL-059 remains active;
public local outcomes, broader review/coverage are open. Next critical-path item:
UL-067 independent Toybox cat producer intake/adoption, then native dash external
command and pipeline/wait/cleanup. Preserve PRF deferrals; do not restart tuning.

UL-067 normal-copy checkpoint (2026-09-07): local source rebuild passes actual
Toybox binary/empty/short copies with four native reclaims and four deliberate
exit-path controls. Evidence: docs/evidence/toybox-native-consumer-2026-09-07/README.md.
CAT-02 has local evidence; overall story stays active. Remaining critical work:
CAT-03/05 delivered usage/error profiles locally; CAT-06 failed/unknown close,
final close-error diagnostic and re-entry treatment; source-built producer and
CAT-08 regressions plus independent review. Current run reuses verified owner
payloads. Continue these release requirements toward native dash; no optional
benchmark/locale refinement is added.

UL-067 error/usage checkpoint (2026-09-07):31 local native cases pass with exact
status/prefix/diagnostic and cleanup oracles; CAT-03/05 now have bounded evidence.
See docs/evidence/toybox-error-usage-consumer-2026-09-07/README.md. Next CAT-06:
pin/review the producer finalizer delivery once its final source/archive/receipt
exists; verify callback output, failed flush/close, private-hook re-entry and the
required final close-error diagnostic. The observed producer plan is in progress,
not acceptance. Full producer/backend rebuild, CAT-08 regressions and independent
review remain required before story closure. Then native dash command/pipeline.

UL-067 finalizer checkpoint (2026-09-07): completed handoff captured;18 finalizer
cases and7 normal-copy regressions pass locally. Evidence:
docs/evidence/toybox-finalizer-consumer-2026-09-07/README.md. CAT-06 stays partial.
Next exact proposal: experiments/toybox-native/FINALIZATION-GAPS.md — final close
diagnostic while stderr remains usable, failed/uncertain diagnostic/close cases,
and a repeat-entry latch preventing outer success. Preserve earlier nonzero status,
no traffic after poison and remote cleanup evidence. Owner opt-in expectations,
full producer/backend rebuild, regressions and independent review remain required.

UL-067 backend checkpoint (2026-09-07): both backends source-rebuilt locally;
complete ELF equality verified against all25 finalizer/cat payloads. Evidence:
docs/evidence/toybox-backend-rebuild-2026-09-07/README.md. Local backend provenance
for these cases is resolved; full producer/regression gate stays open. Close-policy
producer qualification is in progress; completed manifest/source/archive/receipt
required before intake. Its proposed diagnostic is `cat: close failed\n`; review
this explicitly against the local earlier proposal, preserving exact oracles.

UL-067 full producer regression checkpoint (2026-09-07): all213 command cases pass
locally on the captured finalizer revision; source inventory and semantic oracles
unchanged, complete outer cleanup. Evidence:
docs/evidence/toybox-producer-regression-2026-09-07/README.md. Broad command-suite
regression is complete for this revision only. New close-policy intake and its
affected regressions remain required, plus independent review; CAT-06/M3 stay open.

UL-067 close-policy checkpoint (2026-09-07): completed handoff captured;27 local
cases qualify the named bounded CAT-06 diagnostic/uncertainty/re-entry gaps.
Evidence: docs/evidence/toybox-close-consumer-2026-09-07/README.md.209 owned commands
clean up; four semantic mutants reject and accepted outcomes reclaim four tasks.
Candidate diagnostic explicitly selected as `cat: close failed\n`. Remaining:
full CAT matrix and independent review, assess affected new-revision regressions
(prior local213 differs from current producer213). Continue M3 native dash launch/
process/FD integration; do not expand optional utility tuning. Story stays active.

UL-007 startup probe checkpoint (2026-09-07): six host semantic cases pass and the
production probe links with the pinned native SDK. Evidence:
docs/evidence/dash-startup-probe-2026-09-07/README.md. Native NOT RUN. Next capture a
matching owner-reviewed startup identity/signal/FD pair, qualify this probe plus
native denial/cleanup, then actual dash initialization and child exec/wait. Host
false-success controls are ready; they are not producer implementation or native
acceptance. Optional tuning remains deferred; independent review is pending.


UL-067 current-revision regression checkpoint (2026-09-07): all213 native command
cases pass locally on the close snapshot with unchanged source/oracles and complete
outer cleanup. Evidence: docs/evidence/toybox-close-regression-2026-09-07/README.md.
CAT-08 broad revision gap resolved; full actual-applet matrix/independent review
remain. This is not213 upstream cat runs. UL-007 still awaits matching producer
startup support; its consumer probe is prepared. No optional tuning added.

UL-007 startup intake update (2026-09-07): bounded producer pair delivered and
verified; waiting for this delivery is resolved. Snapshot:
build/dash-startup-intake-lzvm3lp3. Next independent native startup reproduction
with matching adapter/SDK/envelope. Evidence:
docs/evidence/dash-startup-intake-2026-09-07/README.md. Producer222 is not consumer
acceptance; full dash signal delivery and fork/exec/wait remain unresolved.


UL-007 native startup checkpoint (2026-09-07): bounded pair independently qualified,
all222 command cases including nine startup cases pass; host tests and cleanup pass.
Evidence: docs/evidence/dash-startup-native-2026-09-07/README.md. Full dash work is in
progress at Aether. Next matched delivery needs actual shell initialization and
exec/wait/pipeline oracles; no full UL-007 completion or independent sign-off inferred.

UL-007 full-dash handoff readiness (2026-09-07): experiments/dash-native/WORKLOADS.md
and workloads.json now bind12 existing reference scripts to candidate native forms,
exact outputs/exits and fixture requirements. All native cases NOT RUN. Next owner
agreement on helper/namespace/resource mappings plus completed full-dash delivery,
then actual shell initialization, child/wait and redirection/pipeline qualification.

## Simplicity adoption and delivery triage

| ID | Status | Work and acceptance | Dependencies / coordination |
| --- | --- | --- | --- |
| UL-080 | done | Adopt unreleased Coding v0.2.0 SE-01–05 as a separate local hash-pinned snapshot; integrate guidance, existing review and integrity gate | docs/evidence/simplicity-adoption-2026-09-07/README.md; released/approved pins unchanged; prospective process adoption only |
| UL-081 | done | Current session SDK/compatibility boundary assessment; implementation remains UL-007 | docs/SESSION-SDK-BOUNDARY.md and docs/evidence/session-sdk-boundary-2026-09-29/README.md: accepted ELF relink and four omission/duplicate controls,30 providers; omitted memory still links and must be component-rejected. Single opt-in runtime closure selected; current driver duplication retained with owned helper, no active path removed. Runtime-owner agreement/sealed bundle, independent review and UL-007/063/M3 follow-ons remain open |

UL-007 mask/descriptor update (2026-09-07): shared public/internal mask and bounded
dup2 independently qualified in227 native command cases/14 startup-family cases.
Evidence: docs/evidence/shell-mask-consumer-2026-09-07/README.md. Source/SDK integrity
and cleanup pass. Next completed custom-handler/process delivery; actual dash and
fork/exec/wait/pipes remain open. UL-081's duplicate-mask concern is resolved for
this bounded producer facade; broader integration selection remains in UL-007.


UL-007 actual dash signal/init checkpoint (2026-09-08): all291 native command
cases pass independently on the captured generated-init snapshot. Four exact dash
lifecycle/rejection checks pass; accepted cases reclaim four tasks over two
generations, skipped signal/init reject client102/103 and owner1501. All545 source
and4311 SDK files retain identity; outer cleanup complete. Evidence:
docs/evidence/dash-init-consumer-2026-09-08/README.md. No failed attempt.
Generated init deliberately exposes PPID -38, unsupported geteuid and empty PWD/
getcwd warning; this is not successful shell startup. Next completed truthful-parent
pair, launcher user metadata and scoped directories, then actual main/exec/wait/
pipelines. Full review, UL-016 and M3 remain open; optional tuning stays deferred.


UL-007 direct-parent checkpoint (2026-09-08): all295 native command cases pass
locally on the completed parent snapshot. Actual musl/generated PPID=4 agrees
with root PID4/parent0; both worker placements pass two generations/four reclaims.
Disabled/self-identity controls reject client104/owner1501. All545 source/4311 SDK
hashes remain unchanged; outer cleanup complete, no local failed attempt. Evidence:
docs/evidence/dash-parent-consumer-2026-09-08/README.md. Fixed launcher lifetime
only; no new authority/reparenting claim. Next user/group metadata and scoped CWD,
then actual main/exec/wait/pipes. Independent review, UL-016/063 and M3 remain open.


UL-007 metadata review checkpoint (2026-09-08): verified the completed AECAT002
proposal packet and12 archived inputs; runtime delivery remains pending. Consumer
cases UL007-META-01–12 are in experiments/dash-native/METADATA.md, all NOT RUN.
Two bounded host inspections confirm the retained Linux-reference main.o omits
the source's !linux UID/GID equality guard before interactive ENV. UL-081 now has
a concrete native-configuration decision before full-main acceptance; this does
not block bounded initvar metadata qualification or prove a shipped vulnerability.
Evidence: docs/evidence/dash-metadata-review-2026-09-08/README.md. Quality passes.
Next completed sender/decoder/getter/native pair, then scoped CWD; no unchanged
295-case rerun, extra startup probe, sibling edit or optional tuning.


UL-007 AECAT002 checkpoint (2026-09-08): original309-case suite passes locally;
final14 metadata serial oracles pass with exact positive/invalid four-reclaim and
publication-mutant105/1501 outcomes. Source/SDK unchanged; complete outer cleanup.
Evidence: docs/evidence/dash-metadata-consumer-2026-09-08/README.md. An incomplete
early live-log inspection is retained separately; final receipt-bound checks pass.
Seven META checklist rows have bounded evidence;03/05/06/07/11 remain partial:
per-getter errno, V2 descriptor composition, truncation boundaries, queued version
body teardown and remaining raw getters. No defects inferred from missing tests.
Next focused coverage and scoped CWD; full-main ENV configuration and exec/wait/
pipes remain gates. No metadata/full-M3 closure or independent review inferred.


UL-007 initial directory consumer checkpoint (2026-09-09): all319 native command
cases pass locally. Ten exact serial checks cover four PWD forms, five malformed
grants and skipped publication106/1501. Accepted/invalid inputs reclaim four tasks;
publication mutant has zero native reclaims. Source/SDK unchanged, outer cleanup
complete, no failed local attempt. Evidence:
docs/evidence/dash-cwd-consumer-2026-09-09/README.md. Scope is private /work and
three stat fields, not a general filesystem. Next directory reply corruption/
truncation/poison teardown, AECAT003 version/truncation, alias and mismatched identity/
PWD controls, plus forced getcwd ENOMEM. Preserve five partial metadata rows,
full-main ENV configuration and actual exec/wait/pipes gates. UL-007/M3 stays open.


UL-007 directory bootstrap rejection checkpoint (2026-09-09): all 323 native cases
pass locally; four independent receipt-bound serial checks verify client110/backend17
in both generations and owner100/four reclaims. Source/SDK unchanged, outer cleanup
complete, one passing native attempt. Evidence:
docs/evidence/dash-cwd-bootstrap-consumer-2026-09-09/README.md. Covered: stdin alias,
16-byte final-record truncation and header-only V2/V3 mismatches. Remaining: other
stream aliases, V1/V3/queued-body mismatches, other truncation boundaries, directory
reply faults/poison/no-further-traffic/teardown, identity/PWD mismatch and forced
ENOMEM. Preserve five partial metadata rows, actual-main ENV configuration and
exec/wait/pipes gates. UL-007/M3 and independent review remain open.

UL-007 actual dash execution checkpoint (2026-09-09): all369 original native cases
pass locally. Nine main/file and18 metadata serial checks pass; four/six-reclaim
success and exact zero-reclaim mutation rejection are distinct. Source549/SDK4311
unchanged; complete outer cleanup, one passing local attempt. Evidence:
docs/evidence/dash-file-consumer-2026-09-09/README.md. Actual dash executes a builtin
command/status7 and opens/reads/parses hello.sh/status0. Five previously partial
metadata observations now have bounded evidence; all12 scoped rows are mapped.
Remaining: V4 admission/alias/exhaustion/stale/fault/lost-reply/service-stop cleanup,
actual-main ENV and unsupported -p, existing argv/signal/syntax and external-command/
exec/wait/redirection/pipeline workloads. UL-007/M3 and independent review stay open.


UL-007 V4 admission checkpoint (2026-09-09): all384 native cases pass locally;
24 exact final serial checks pass, including14 malformed-root110/17/17 outcomes
with six reclaims, early-publication113/1501 with zero reclaims, and prior nine
main/file cases. Source549/SDK4311 unchanged; complete outer cleanup; one passing
native attempt. Evidence: docs/evidence/dash-file-admission-consumer-2026-09-09/README.md.
Selected fields, EOF192/208/223 and header-only V3/V4 mismatch now have local evidence.
Next independent opens/exhaustion/shared-offset/stale controls, queued V4 bodies,
malformed/lost replies and service-stop recovery, then ENV/-p and existing native
workloads/exec/wait/redirection/pipelines. UL-007/M3 and independent reviews stay open.


UL-007 file-description checkpoint (2026-09-09): all387 native cases and27 exact
final serial checks pass locally. Positive client checks independent/shared offsets,
CLOEXEC,16-FD exhaustion/no-traffic closes, EOF, reopen/stale/wrong-binding denial,
root/write-rights/missing-name denial and six-open exhaustion without poison.
Six opens/nine reads, no live records, two generations/six reclaims. Offset and
reference mutants fail114/1501 with zero reclaims. Prior24 admission/main cases
still pass. Source549/SDK4311 unchanged; complete outer cleanup; one passing local
attempt. Producer's failed suffix-length expectation retained separately. Evidence:
docs/evidence/dash-file-descriptions-consumer-2026-09-09/README.md. Next queued V4
bodies, malformed/lost replies and confirmed service-stop recovery, then ENV/-p and
actual argv/signal/syntax/exec/wait/redirection/pipelines. UL-007/M3 stays open.


UL-007 known-result file-reply recovery checkpoint (2026-09-09): all397 native cases
and37 final serial checks pass locally. Six corrupted/cut client replies after
checked backend open/read/close require EIO/poison/no later traffic and known-record
retirement after client1, then six reclaims. Two V3/V4 queued mismatches leave15
unread bytes and reject110 with six reclaims. Omitted retirement1599 and wrong
witness108/1501 reject with zero reclaims. Source549/SDK4311 unchanged, complete
outer cleanup; one passing attempt. New owners max8056/8192 bytes. Evidence:
docs/evidence/dash-file-recovery-consumer-2026-09-09/README.md. Next unknown backend
reply outcomes and confirmed service-stop cleanup without replay, then ENV/-p and
actual argv/signal/syntax/exec/wait/redirection/pipelines. UL-007/M3 stays open.


UL-007 malformed-backend intake preparation (2026-09-09): static review and four
exact NOT RUN consumer oracles are ready at
docs/evidence/dash-backend-intake-2026-09-09/README.md. Producer401-case run is
in qualification/unsealed at capture; latest local runtime remains397. Require
confirmed stop record before local-description clear/reclaim, no normal file-exit
log assumption, omitted-stop1601 failure and unchanged8192-byte owner bound.
Compare final sealed sources and retain failed image/size/lifecycle attempts before
runtime intake. Missing/partial/backend-timeout witnesses remain follow-ons; this
review does not close backend recovery, actual-main ENV or external-process gates.


UL-007 malformed-backend checkpoint (2026-09-10): all401 native cases and41 exact
final serial checks pass locally. Malformed complete open/read/close replies cause
poison/client1, confirmed service stop before description clearing, and six reclaims
across two generations. No normal slot2 exit line is expected; owner checks retained
stop143/kind3. Omitted stop rejects1601 with zero reclaims. Source549/SDK4311 unchanged,
complete outer cleanup, one passing native attempt; owner bound8192 preserved.
Evidence: docs/evidence/dash-backend-consumer-2026-09-10/README.md. Earlier pending401
notes are historical. Next consolidated431-case command intake covers later producer
EOF/timeout, ENV, syntax and helper progress; review changed4096-attempt polling.
These are producer-only until reproduced. Public-fork callbacks are separate143-
connection candidate evidence; wait/exec remain owner work. No full M3 acceptance.


UL-007 consolidated dash checkpoint (2026-09-10): independently reproduced all
431 command cases and six shared-transfer connection regressions. All 71 selected
final serial checks pass. Backend EOF/partial/silent/late recovery, actual ENV
loading/suppression, unsupported -p, syntax-error and unchanged helper via explicit
launcher now have bounded local evidence. Source/SDK integrity and cleanup pass;
new owner maximum 8152/8192 bytes. Evidence: docs/evidence/dash-helper-consumer-2026-09-10/README.md.
Earlier pending 431-case intake notes are historical. Next review/reproduce the
verified public-wait producer candidate separately; its 147 connections/five launch
cases are not local acceptance. Dash wait4/wait3, non-normal wait/reply controls,
exec/vfork, external commands, redirection and pipelines remain gates. No full M3,
installed SDK, source-trust or independent technical/reader acceptance follows.


UL-007 serial-shell consumer checkpoint (2026-09-11): 303 native cases pass
(241 connections, five launch, two console, 32 composed-init, 23 init-large).
Six independent serial protocols pass. Actual configured dash forks/executes /next,
waits for child72, returns to a prompt, prints status72 and exits0 then7 with six
reclaims across two sessions. Original-tee/wrong-input/cleanup/wrong-exit controls
reject as specified. Evidence: docs/evidence/dash-serial-consumer-2026-09-11/README.md.
All 578 source/4311 SDK hashes remain unchanged; serial owners max9528/16384.
Retain the incorrect aggregate-count assertion, rejected relative host invocation
and missing-doc host failure. A separate host tree adds a pinned inventory document
and passes Zig/host/workflow checks including99 Python tests. Native inputs unchanged.
Earlier public wait/exec intake notes are historical for this bounded single-child
path. Repeated external children per shell, full workload scripts, pipes/redirection,
TTY, persistence/sys-init/package assembly and independent review remain open.
Next completed repeated-child lifetime delivery and matched consumer qualification;
no full M3, installed SDK, release or fresh SMP/M4 acceptance.


UL-007 repeated-command/redirection checkpoint (2026-09-11): all 254 native cases
(247 connections, five launch, two console), 12 independent serial protocols and
host checks including 99 Python tests pass in one local attempt. One dash parent
runs three external children with terminal/wait-ack disposal before slot reuse;
builtin >&2 and restored stdout, exact 72/60/19 byte accounting and six reclaims
pass. Stale token/bootstrap and raw closed fork/exec encoding controls reject as
specified. Source579/SDK4311 integrity and host cleanup pass; owner max9944/16384.
Evidence: docs/evidence/dash-redirect-consumer-2026-09-11/README.md. Kernel/build and
SDK/dash object pins unchanged; previous init-bound evidence reused, not recounted.
Earlier one-child-total limits are historical for this bounded three-command path.
Next native pipe adapter/dispatcher and terminal-driven endpoint retirement, then
unchanged DASH-substitution; pipe host core is not native support. Consumer intake
requirements are prepared in that evidence/pipe-next.md. Full scripts, concurrent
pipelines, file redirection, TTY, persistence/assembly and independent review remain.
No full M3, installed SDK or release acceptance follows.


## 2026-09-11 — UL-007 pipe core consumer host qualification

The pinned unconnected pipe core passes 12 local producer host cases and 32
independent consumer chunk schedules covering backpressure/retry, byte order,
terminal-before-collection EOF, stale child denial and pending-reply retirement.
Five semantic mutants fail as expected; x86_64 no_std object generation passes.
[Evidence](../docs/evidence/pipe-core-consumer-2026-09-11/README.md) preserves the
initial formatting failure and successful fresh attempt. This is host-only;
UL-007/M3 remains open. Next action: consume the Aether native pipe dispatcher and
adapter delivery, then qualify unchanged substitution and remaining pipe/signal
boundaries. Prior native redirection evidence remains unchanged. Independent
technical/security/reader review remains pending.


## 2026-09-13 — UL-007 unchanged argv/signal native consumer checkpoint

DASH-argv and DASH-signal-table now pass locally through the private native
producer adapter. Seven focused cases and seven independent serial checks pass;
consumer scripts/helper/manifest match byte for byte. Positives require two
child0/parent0/backend17 lifetimes and six reclaims. Argument/environment, skipped
helper, dropped post and bypassed PID scope reject exactly as selected.
Evidence: docs/evidence/dash-argv-signal-consumer-2026-09-13/README.md.
Native run passed first attempt; a retained filename error affected retention
only and was corrected without rerun. Full local 287-case regression is NOT RUN.
Next: remaining changed pipe/exec controls and consolidated producer handoff.
Original substitution/pipeline/file/TTY/assembly gates and independent review stay
open; UL-007/M3 and public SDK/release acceptance are not complete.


## 2026-09-14 — UL-007 background wait consumer checkpoint

Unchanged DASH-wait passes locally: helper7/parent0/backend17 twice, exact owner
readback and six reclaims. All 13 focused native cases and 13 separate transcript
comparisons pass, including before/after parking, stop, ignore/block, duplicate
notification and stale-parent replacement controls. Consumer script/helper/manifest
match local bytes. Source/SDK integrity and owned cleanup pass on the first run.
Evidence: docs/evidence/dash-wait-consumer-2026-09-14/README.md.
This is bounded private-adapter acceptance; no full314, matched command-runner or
scheduler replay was performed here. Next matched phase-one replay and descriptor
closure qualification, then remaining workloads and changed-path regression.
General signals, eventual unblock, writable files/TTY/persistence/assembly and
independent reviews remain open. UL-007/M3 is not complete.


## 2026-09-14 — UL-007 descriptor closure consumer checkpoint

Unchanged DASH-fd-closure passes locally: descriptors3–63 closed after real exec,
owner readback, child0/parent0/backend17 twice and six reclaims. All three native
cases and transcript comparisons pass; injected FD3 and corrupt wait status reject
exactly. Consumer byte identity, source/SDK integrity and owned cleanup pass on the
first attempt. Evidence: docs/evidence/dash-closure-consumer-2026-09-14/README.md.
Corrected phase-one dependencies and256 source/346 support members verify read-only;
this is intake, not execution. Next matched431 command-runner/287 connections replay
with the corrected source set. Full290 closure regression, writable fd-leak-control,
other unchanged workloads, public SDK/reviews and M3/assembly remain open.


## 2026-09-14 — UL-007 matched phase-one consumer qualification

Corrected matched phase-one replay passes locally:431 command-runner plus287
connections,718 native cases on identical242 harness source hashes. All208 startup
cases indexed; ten exact syntax/argv/signal trace checks pass. Host checks including
100 Python tests pass. All602 restored source/support files and4311 SDK files stay
unchanged; all started commands have complete cleanup. Both native suites passed
first attempt. A retained collector PASS-marker mismatch was corrected separately
without native rerun. Evidence: docs/evidence/dash-phase-one-consumer-2026-09-14/README.md.
This closes the fresh matched private phase-one runtime replay gap. It does not
close independent reviews or UL-081 public SDK boundary acceptance. Next integrate
newer wait/closure sets with matching broader regression and remaining unchanged
workloads. General signal/TTY, writable files, persistence/assembly and full
UL-007/M3 remain open. No new release or installed SDK claim.


## 2026-09-14 — UL-007 current acceptance and failed-exec intake

Current matrix: experiments/dash-native/ACCEPTANCE.md. Five of12 unchanged scripts
have bounded local native evidence (argv, signal-table, syntax-error, wait,
fd-closure); seven remain unqualified. Verified script/stdout/helper pins and three
local evidence seals. Historical workloads.json remains unchanged. Evidence:
docs/evidence/dash-acceptance-index-2026-09-14/README.md.
Next failed-exec owner proposal: experiments/dash-native/FAILED-EXEC.md. Captured
latest exec-stage treats /inputs/not-executable as absent; the unchanged script
needs actual missing127/non-executable126 distinction and cleanup. No sibling
implementation or new native acceptance. Producer suspend-recovery matching runner
is incomplete after timeout; avoid competing long runs until its matched handoff.
Full M3, SDK/reviews, remaining workloads and assembly stay open.


## 2026-09-14 — UL-007 matched recovery consumer qualification

Matched316 connections and431 command-runner cases pass locally, sequentially,
on identical250 harness source hashes. All208 startup and25 selected transcript
checks pass; host includes101 Python tests. All611 source/support and4311 SDK
files remain unchanged. Timings1072.68/1463.65seconds are within1800 review ceiling;
owned cleanup complete. Evidence: docs/evidence/dash-recovery-consumer-2026-09-14/README.md.
This closes newer recovery full-set replay; previous timeout remains historical.
Full artifacts are compacted with verified readback and relocation mappings to
preserve the user's cleanup preference. No sibling/SDK installation change.
Five unchanged scripts remain qualified; failed-exec is an owner contract awaiting
implementation (two fresh VMs, two sequential children/four reclaims each proposed
by Aether; actual native admissions still require measurement). Next consume that
native delivery and controls. General signals/TTY, writable filesystem, persistence,
SDK/reviews and full UL-007/M3/assembly remain open.


## 2026-09-15 UTC — UL-007 failed-exec consumer qualification

Unchanged failed-exec now passes locally. Two fresh VM positives each give real
child127/gen1, child126/gen2, parent0/backend17 and four reclaims; all five controls
reject exactly. Sequential6 focused+322 connections+431 command-runner pass (759
executions), with252 matching full-suite source hashes,208 startup and37 trace
checks. Host includes101 Python tests;613 source/support and4311 SDK files unchanged.
Full timings1019.35/1423.47seconds meet1800 review ceiling. No local retry.
Evidence: docs/evidence/dash-failed-exec-consumer-2026-09-15/README.md. New outputs
are archived/readback-verified before unpacked copies and caches are removed.
Current matrix now6/12 unchanged scripts qualified; failed-exec is no longer a
waiting item. Next scratch-backed fd-leak-control/redirection with actual dash
admissions; C/host prerequisites do not qualify scripts. General signals/TTY,
persistence, SDK/reviews and full M3/assembly stay open. No sibling changes.


## 2026-09-15 — UL-007 scratch consumer intake

Verified41 sealed producer fork/owner/helper packet members and all12 unchanged
workload pins. experiments/dash-native/SCRATCH.md records live-FD9 identity,
helper95/parent22/empty-output, shared-offset AB and independent write-denial
oracles. No native profile selects the new helper yet; final owner admission
integration and matched full handoff precede local replay. Current acceptance
remains6/12. Evidence: docs/evidence/dash-scratch-intake-2026-09-15/README.md.
No native tests or sibling changes in this intake; SDK/reviews and M3 stay open.


## 2026-09-23 — UL-007 scratch and substitution consumer qualification

Scratch:11 focused plus355 full connections pass on266 matching harness source
hashes;22 exact lifecycle/PASS checks and104 host tests pass. Full run1163.96s
meets1800s review ceiling. Source/support631 and SDK4311 pins unchanged. Evidence:
docs/evidence/dash-scratch-consumer-2026-09-23/README.md.
Substitution:3 focused cases and3 exact transcript checks pass on later268-source
fixture;104 host tests pass,633 source/support and4311 SDK files unchanged.
Evidence: docs/evidence/dash-substitution-consumer-2026-09-23/README.md.
All local runs pass first attempt with complete owned cleanup. Archive/readback
verification precedes removal of new unpacked suites and compiler caches.
Current per-script matrix is10/12 across separately pinned private fixtures.
Next local regression is the later358 connections fixture; matching command-runner
producer/consumer coverage also remains pending. Pipeline and early-reader await
actual unchanged-script delivery; current incremental owner work is prerequisite.
Independent reviews/SDK, general signals/TTY, persistence and full M3/R1 remain
open. No sibling implementation or released pin changed.


## 2026-09-23 — UL-007 full substitution connections regression

All358 connections cases now pass locally on the exact268-source substitution
fixture. Fourteen exact scratch/substitution lifecycle/PASS comparisons pass;
all358 serials retained. Source/support633 and SDK4311 pins unchanged; owned
cleanup complete. Elapsed1148.42s meets1800s review ceiling. Prior104-test host
qualification reused after byte/tool verification, not rerun. No local retry.
Evidence: docs/evidence/dash-substitution-regression-2026-09-23/README.md.
Archive/readback verification precedes removal of the new unpacked suite/cache;
prior sealed evidence and archives remain unchanged. This closes the later358
local replay gap. Acceptance stays10/12 across bounded private fixtures.
Next dependency: matching command-runner producer/consumer qualification and
actual unchanged pipeline/early-reader delivery. Current Aether pre-exec intake
is integration groundwork, not consumer-script acceptance. SDK/independent reviews,
general signals/TTY, persistence and full M3/R1 remain open. No sibling changes.


## 2026-09-24 — UL-007 next integration boundary

Pipeline/early-reader and matching101 capacity/358 connections/431 runner replay
now pass locally; per-script matrix12/12. Evidence:
docs/evidence/dash-parent-consumer-2026-09-24/README.md. UL-007 remains open.
Next owner delivery must compose the parent-driven pipeline with existing serial
exec/substitution and native runtime in one session; userland then qualifies that
actual composed path. Preserve bounded argv/environment/namespace authority and
signal/stack limits rather than substituting unsupported successful operations.
UL-081 handoff follow-on: include the updated tests/test_build_policy.py in future
host-support delivery. This replay pinned its missing one-line capacity classification
separately; failed host/collector attempts remain retained. No sibling edit occurred.
Independent SDK/source/reader reviews, general signals/TTY, persistence, package
execution and sys-init assembly remain unresolved and are not waived by12/12.


## 2026-09-24 — UL-007 composed-session handoff prepared

SESSION-01–06 in experiments/dash-native/SESSION.md now supplies a pinned positive
script and expected streams. Owner delivery must establish one parent, child/EOF
status, exact admissions/copies/reclaims, mutation outcomes and reviewed bounds
before consumer native replay. All six cases NOT RUN. Include current host-support
test in the sealed delivery (UL-081). Then add early-reader, failed exec, scratch
and real serial-input composition. No sibling implementation authority is inferred.


## 2026-09-24 — UL-007 serial pipeline accepted; forwarding successor available

Independent first serial pipeline acceptance now has898 passing native cases and
29 lifecycle checks (docs/evidence/dash-serial-pipeline-consumer-2026-09-24).
Next consume sealed Aether shell-streams-2026-09-24. Its simpler forwarding and
prospective session-lifetime review are producer progress, not local acceptance.
SESSION-01–06 still needs implemented reusable lifetimes and the entire composed.sh
execution; retain owner review of proposed counts/limits before native consumption.
UL-081 shared SDK and independent reviews, full M3/R1 remain unresolved.


## 2026-09-24 — UL-007 forwarding accepted, reusable-session delivery next

Sealed shell-streams consumer evidence now passes105 native cases/110 host tests
and11 independent controls. Fixed output captures no longer block this bounded
serial workload. Full SESSION-01–06 still needs native reusable jobs, lifetimes,
authenticated identity and exact separate-stream/lifecycle oracles. Aether's current
session-channel core is host-tested with no native caller; do not replace the full
unchanged composed.sh requirement with additional manual single-job witnesses.
Prior898 regression stays prior qualification; changed SESSION inputs need new
matching consumer/producer evidence. UL-081 SDK and independent reviews stay open.


## 2026-09-25 — UL-007 composed SESSION independently qualified

The unchanged complete composed.sh now passes SESSION-01–06 under private
AENMX007/ABI21: three parent lifetimes,27 copies,21 helper execs,24 image admissions
and30 zero-status terminal records/reclaims; exact separate65-byte stdout and
19-byte stderr per parent. All910 matching native cases pass (121 capacity,358
connections,431 runner), plus115 Python and configured Zig/Rust host checks.
Eight independent SESSION cases,14 prior lifecycle comparisons and25 checker
rejection controls pass. Runtime293 hashes match;661 source/support and4311 SDK
regular files remain pinned. Six complete linked owners match the audited producer
ELFs; maximum inspected stack depth3688/4088, not a formal safety proof.
Native suite times407.74/1140.31/1441.82s meet1800s review ceilings; process cleanup
complete. Native and host suites passed first execution. One collector selector
error was corrected and retained without changing runtime or expected outcomes.
Evidence: docs/evidence/session-consumer-2026-09-25/README.md. Current acceptance:
experiments/dash-native/SESSION-ACCEPTANCE.md; original proposal/input pins unchanged.
Next: compose early-reader recovery, failed exec, scratch and real serial input.
UL-081 shared SDK and independent reviews, UL-008/009 TTY, persistent filesystem,
package/sys-init assembly and full UL-007/M3/R1 remain open.


## 2026-09-25 — UL-007 recovery composition handoff ready

Aether has acknowledged SESSION-01–06 acceptance and requested the next consumer
inputs. Prepared experiments/dash-native/SESSION-RECOVERY.md, RECOVERY-01–06, a
new pinned early-reader recovery script and exact stdout/stderr. It runs a healthy
external command and pipeline after EPIPE/pipefail recovery in the same parent,
then checks descriptor closure; repeat across three parent generations.
Dash syntax and ShellCheck pass with owned cleanup. Host/native execution remains
NOT RUN. Evidence: docs/evidence/dash-session-recovery-plan-2026-09-25/README.md.
Original SESSION inputs/evidence remain unchanged; prior910 cases were not rerun.
Next: Aether owner review, resource/phase oracle reconciliation, implementation and
sealed matching producer delivery, then independent userland replay. No sibling
implementation authority is inferred. Failed-exec, scratch and serial composition,
UL-081 SDK/reviews, full M3/R1 and other integration gates remain open.


## 2026-09-25 — UL-059/081 sustained-command dependency reviewed

Current Aether SI-07 prototype reaches generation3 then correctly hits the legacy
userland two-generation restriction. Reviewed carrier, runner/child bootstrap,
admission, collection and terminal-exit receipt checks. Proposed an explicitly
versioned private profile in experiments/command-runner/SUSTAINED.md: bounded
nonzero16-bit epochs, separate version/receipt tags, exact cohort identity and
retirement before wrap. Owner review is pending; no runtime decoder changed.
All458,745 proposed identities are distinct; a blind-widening collision is reproduced.
Legacy648 role cases and28,159 result assertions pass under host UBSan with complete
owned cleanup. Evidence: docs/evidence/sustained-command-contract-2026-09-25/README.md.
Next: owner reconciliation and affected UL-063 review, opt-in implementation, new
controls and rebuilt runner/bytecount inputs, then matching native qualification.
No sustained native acceptance or rebuilt input delivery is claimed. The separate
dash recovery handoff remains ready; full M3/R1 and independent reviews stay open.


## 2026-09-25 — UL-059/063/081 executable sustained decoder proposal

Host-only candidate patch now passes2,592 role cases,37,716 result assertions and
all65,535 epoch peer checks, including old/new wire rejection and an intentional
mixed-link failure. Unchanged legacy648/28,159 controls pass. Retained evidence:
[decoder experiment](../docs/evidence/sustained-decoder-2026-09-25/README.md).
Default runtime sources and accepted payloads are unchanged. Scoped pure-decoder
source assessment does not close UL-063. Next: reconcile owner contract, finish
adapter/caller review, implement/bootstrap-test full-width identity and NIO2,
build versioned runner/bytecount and independently consume matching native delivery.
Native sustained execution, five-cycle/shutdown acceptance and owner/reader review
remain pending. The dash recovery workload remains independently ready for delivery.


## 2026-09-29 — UL-007 independent recovery composition accepted

RECOVERY-01–06 now pass for private AENMX007/ABI21: unchanged script through three
native dash parents, actual EPIPE/pump42 followed by healthy argv and pipeline,
closed descriptors, exact49-byte stdout/20-byte stderr and24 terminal/reclaims.
All128 capacity + five legacy command cases and119 Python/configured Zig/Rust
host checks pass; seven independent comparisons and36 rejection controls pass.
Evidence: [recovery consumer](../docs/evidence/recovery-consumer-2026-09-29/README.md).
Current matrix: [recovery acceptance](../experiments/dash-native/RECOVERY-ACCEPTANCE.md).
The replay export omitted the legacy driver/input bundle; an explicit21-file
historical supplement matches its manifest and the delivery's import digest.
No runtime changes or relaxed inputs. Next: failed-exec, scratch and serial
composition; separately finish SI-07 versioned bootstrap and rebuilt command
inputs. Full UL-007/M3/R1, shared SDK and independent reviews remain open.


## 2026-09-29 — UL-007 failed-exec session input ready

Prepared [SESSION-FAILED-EXEC](../experiments/dash-native/SESSION-FAILED-EXEC.md):
missing127 and denied126 followed by healthy argv/pipeline and descriptor/PID/
parent-stderr checks in the same shell, repeated across three native parents.
Original syntax/ShellCheck and seven explicitly relocated host references pass.
Evidence: [preparation](../docs/evidence/dash-failed-exec-session-plan-2026-09-29/README.md).
Initial host linker failure is retained; corrected build environment passes without
changing target inputs. Native EXEC-SESSION-01–06 remain NOT RUN. Current session
adapter's local non-helper EACCES rejection must become owner-backed lookup/denial;
no fake pathname result can satisfy acceptance. Expected21 copies/12 replacements/
15 admissions/24 terminal-reclaims need owner reconciliation within existing bounds.
Next: owner implementation with complete export/negative oracles, then independent
replay. Scratch/serial composition, SI-07, shared SDK and full M3/R1 remain open.


## 2026-09-29 — UL-007 failed-exec session independently accepted

EXEC-SESSION-01–06 pass for private AENMX007/ABI21. Three unchanged dash parents
recover from owner-backed missing127/denied126 and continue with healthy argv,
pipeline, descriptor/PID and parent-stderr checks. All137 capacity + five legacy
command cases,123 Python/configured Zig/Rust host checks, nine independent
comparisons and56 rejection controls pass. Exact60/25-byte streams,15 admissions
and24 terminal/reclaims; slot2 ends at15. All17 owners match final stack/image
bindings (maximum3768/4088). No consumer runtime retry or input relaxation.
Evidence: [failed-exec consumer](../docs/evidence/failed-exec-session-consumer-2026-09-29/README.md).
Current matrix: [failed-exec acceptance](../experiments/dash-native/FAILED-EXEC-ACCEPTANCE.md).
Original native and final delivered checker hashes are explicitly reconciled;
fresh legacy replay qualifies delivered sources without claiming old receipt
identity. Next: scratch and real serial compositions; independently SI-07 complete
bootstrap/transport and rebuilt runner/bytecount. UL-007/M3/R1, shared SDK and
independent reader reviews remain open.


## 2026-09-29 — UL-007 scratch session input ready

Prepared [SESSION-SCRATCH](../experiments/dash-native/SESSION-SCRATCH.md): truncate
stale data, preserve shared-offset alias lifetime, deny protected write, reopen
and readAB/EOF, then healthy argv/pipeline, closed descriptors, same PID and stderr.
Original syntax/ShellCheck and11 explicitly relocated host references pass, including
wrong file state, allowed/skipped denial, missing reader, wrong environment, FD leak,
wrong bytes and closed stderr. Evidence: [scratch preparation](../docs/evidence/dash-scratch-session-plan-2026-09-29/README.md).
Native SCRATCH-SESSION-01–06 remain NOT RUN. Expected three-parent21 copies/15 helper
replacements/18 admissions/24 reclaims require owner resource/lifetime reconciliation
and fresh linked code/stack review within current bounds. Next owner integration,
sealed complete delivery and independent replay. SI-07 complete bootstrap/transport,
real serial composition, shared SDK/reviews and full M3/R1 remain open.

## 2026-09-29 — UL-007 scratch session independently accepted

SCRATCH-SESSION-01–06 pass:149 capacity plus five legacy native cases;127 Python
and configured Rust/Zig checks. Twelve independent comparisons and100 rejection
controls pass.26 locally rebuilt owners match sealed raw/ELF hashes, max3896/4088
estimated stack. Exact52/19-byte streams across three parents;21 copies,15 helper
replacements,18 admissions,24 terminal/reclaims. Full owner-local data/denial
oracles reviewed with native semantic controls. Only the delivered host checker
changed after the producer native receipts; exact source reconciliation retained.
Evidence: [scratch consumer](../docs/evidence/scratch-session-consumer-2026-09-29/README.md).
Next real serial composition; SI-07 complete transport/rebuilt payloads, SDK,
independent reviews and full M3/R1 remain open. Original pinned inputs unchanged.

## 2026-09-29 — UL-007 real serial SESSION input ready

[Serial handoff](../experiments/dash-native/SESSION-SERIAL.md) preserves the accepted
SESSION commands as three prompt-driven lines. Eight relocated host stdin controls,
syntax and ShellCheck pass; native NOT RUN. Exact65/19-byte program streams and
90-byte combined UART per parent are pinned. Require fresh-prompt input gating,
state across prompts, phase child cleanup, owner UART authority/short transfers,
EAGAIN and explicit cancellation with confirmed reclaim.27 copies,21 replacements,
24 admissions and30 terminal/reclaims are planned across three parents; exact native
map/control codes and fresh resource review remain owner-delivery prerequisites.
Evidence: [serial preparation](../docs/evidence/dash-serial-session-plan-2026-09-29/README.md).
Next Aether implementation/delivery then independent SERIAL-SESSION-01–06 replay.
No native acceptance, general TTY/hangup, SI-07, SDK or full M3/R1 closure is claimed.

## 2026-09-29 — UL-007 real serial SESSION independently accepted

SERIAL-SESSION-01–06 pass for private008/ABI23: one fresh complete160-case capacity
run, five legacy and four envelope/ABI cases;132 Python/configured host checks.
Eleven independent comparisons and151 counterexamples pass.35 local owner raw/ELF
pairs match sealed audits; max3944/4088 estimated stack, serial max3832. Three
parents/nine prompted inputs retain x/PID and exact65/19-byte streams plus6 prompt
bytes,90 UART.27 copies,21 replacements,24 admissions,30 terminal/reclaims.
Source reconciliation preserves producer incomplete attempts and final host-only
checker correction. Consumer preflight prompt-end correction retained; native
suites passed first attempt. Evidence: [serial consumer](../docs/evidence/serial-session-consumer-2026-09-29/README.md).
Next UL-081 shared SDK boundary and reader reviews; SI-07 complete transport and
rebuilt payloads, general TTY/persistence/packages/sys-init/full M3/R1 remain open.

## 2026-09-29 — UL-081 assessed; native continuation blocked on runtime/review

Current accepted serial link reproduced byte-for-byte. Four omission/duplicate
experiments and30 provider mappings pass: missing facade/process and duplicate
facade reject; omitted memory adapter still links through musl, yielding a different
unqualified ELF. [SDK boundary](../docs/SESSION-SDK-BOUNDARY.md) requires exact component
admission and an owner-agreed, sealed application/runtime split before SSDK-01–06.
UL-081's assessment is done; no runtime implementation or review approval is implied.
Evidence: [boundary audit](../docs/evidence/session-sdk-boundary-2026-09-29/README.md).
Small driver duplication/owned helper retained, no active path removed; UL-063 broad
source audit stays open. First static sentinel check corrected with retained attempt.
Independent [reader packet](../docs/quality/SESSION-RUNTIME-REVIEW.md) is ready, review
pending. Further M3 integration waits for runtime-owner agreement/delivery and
independent review; SI-07 separately waits for complete transport/rebuilt payloads.

## UL-007 runtime ownership cleared — 2026-09-29

The maintainer assigned bounded libc/POSIX runtime implementation to userland.
Proceed with experiments/session-runtime: separate application startup/path policy,
retain qualified mechanism inputs, enforce explicit component closure, rebuild and
exercise native serial behavior. SSDK-01–06, independent review and broader
UL-007/063/M3 remain open. SI-07 remains a separate versioned-lifetime integration.

## UL-007 extraction/candidate checkpoint — 2026-09-29

Userland runtime ownership agreed and implemented in experiments/session-runtime.
Evidence: docs/evidence/session-runtime-extraction-2026-09-29/README.md.49 fresh
native executions and49 independent comparisons; seven component/eight malformed
bundle controls; sealed standalone008 candidate rebuilds identical tested ELFs.
Next actual independent technical/reader findings and SSDK-01–06 disposition.
Preserved007 compatibility recompiles do not advertise a007 SDK bundle. Full
UL-007/063/M3/R1 remain open; SI-07 versioned lifetime composition is separate.

## UL-007 build dependency selection fixed — 2026-09-29

Evidence: docs/evidence/session-runtime-build-imports-2026-09-29/README.md. The old
builder could reuse a cached validator and admit an omitted memory component.
The corrected builder loads exactly verified support files, preserves caller import
state, rejects that omission and reproduces the native-tested parent/helper bytes.
Five host cases pass; native sources/helper and prior evidence remain unchanged.
Independent review/SSDK disposition remains pending. Aether has cleared its SI-07
v2 protocol design review; next prepare full bootstrap/transport and runner/bytecount
closure after affected UL-063 source review, then matched owner/native qualification.

## SI-07 client checkpoint, 2026-10-03 (UL-058/UL-063)

[Opt-in client delivery](../docs/evidence/sustained-runtime-2026-10-03/README.md)
completes maintained bootstrap/transport and rebuilt runner/bytecount with scoped
source review and host/static evidence. Default legacy ELF bytes are preserved.
Acceptance remains incomplete: matching Aether runtime hooks, five real cycles,
65536pre-effect rejection, native cleanup/authorized halt and independent userland
consumption remain required. Independent review and broader UL-063 remain open.

## SI-07 matched checkpoint consumed — 2026-10-03

[Independent consumer](../docs/evidence/si07-consumer-2026-10-03/README.md) passes nine
fresh native replays, including five useful cycles1–5, seeded epoch boundaries,
pre-admission exhaustion, both parent mismatches and cohort divergence.242 semantic
trace corruptions reject; exact ISO/client/owner identities and scoped resource
models are bound. The missing-input/generation3 gate is closed. sys-init BG-067
owns consuming sustained policy and outstanding-work settlement; remaining native
child-profile/malformed/stale/foreign/partial/poisoned-close schedules, reader/SDK
and broader UL-058/063/M3/R1 acceptance remain open.

## Quiescent SI-07 loop consumed — 2026-10-03

[Seven fresh userland replays](../docs/evidence/si07-loop-consumer-2026-10-03/README.md)
confirm initial/between-cycle shutdown and six useful cycles beyond the old cutoff,
buffered intent after cleanup, invalid/busy/exhausted denial.179 trace corruptions
reject; exact producer/client/owner identities are bound. Bounded development has
no established external blocker. Sys-init BG-067 continues partial/unknown reply
and cleanup-failure controls locally; remaining native userland schedules, SDK
reader/disposition and full UL-058/063/M3/R1 remain open.

## SI-07 failure controls consumed — 2026-10-03 (UL-058/063)

[Four fresh userland native replays](../docs/evidence/si07-errors-consumer-2026-10-03/README.md)
pass: real fragmented replies complete; accepted write/reply-reader loss prevents
replay/completion/halt; actual close/reclaim errors retain Unknown ownership and
deny cleanup/stop/start replay.183host trace corruptions reject. Exact sealed
producer/base/client/owner/tool/ISO closure and scoped resource models are bound.
No maintained runtime or sibling changes. Bounded continuation is unblocked.
[Current disposition](../docs/SI07-DISPOSITION.md) separates established SUSTAIN
requirements from broader native schedules, useful-session/wait policy, SDK reader
review/disposition and full UL-007/058/063/M3/R1. No production recovery claimed.

## UL-007 minimum Python builder repaired — 2026-10-03

[Actual minimum/current interpreter evidence](../docs/evidence/session-runtime-python310-2026-10-03/README.md)
reproduces two Python3.10 hashing failures and repairs both maintained streaming
hash paths. Pinned3.10.21/3.14.7 each pass ten controls and rebuild exactly the
previously native-qualified parent/helper. New sealed candidate preserves all
other recipe/SDK/runtime/helper inputs; historical evidence is unchanged.
SSDK-01 scoped build evidence improves; independent technical/reader disposition,
SSDK-02–06, native enforcement schedules and full UL-007/063/M3/R1 remain open.
No sibling or native runtime changes and no new QEMU claim.

## Maintained bootable lab-kit checkpoint — 2026-10-03 (UL-007/012)

[Lab-image builder](../experiments/lab-image/README.md) consumes a sealed corrected
SDK, rebuilds exact clients, verifies all actual ISO components and produces a
UEFI VM kit with firmware, workload, notices and receipts. Minimum/current Python
builds and12semantic controls pass. A fresh boot runs three dash parents/nine
prompt-driven commands with exact bytes/lifetimes and checked cleanup. No kernel,
native runtime, sys-init/package policy or grant change. Physical hardware and
unrestricted/persistent/TTY service integration remain open.

Maintainer explicitly directs continued coding and defers SSDK-06 reader review
until later lab inspection. That review remains incomplete; no development stop
or SDK/release approval is inferred. Next code: extend the bounded lab workload
through an explicit owner contract, then assembled supervision/package/storage
interfaces. Userland must not silently widen the ABI23 fixture or edit siblings.
Evidence: docs/evidence/lab-image-2026-10-03/README.md. Full M3/M5/R1 remains open.

## ABI24 endpoint-wait checkpoint — 2026-10-03 (UL-007/081/012)

[Consumer evidence](../docs/evidence/session-channel-wait-consumer-2026-10-03/README.md)
qualifies explicit009 wait-aware clients against the sealed wait kernel/lifecycle
owner, preserving default008 whole ELF bytes. Native delayed dash input, exact
program/serial/identity/cleanup, host fragmentation/error mutants and actual
minimum/current interpreter SDK/lab profile controls pass. The maintained lab
builder supplies matched009 and retains008 scope. Independent review remains
pending; SSDK-06 deferral does not pause local coding.

Next: [sys-init composition handoff](../docs/ABI24-SESSION-HANDOFF.md), actual
assembled009 launch/readiness/terminal/reclaim/halt and delayed-input controls.
Userland wait-EINTR injection, broader backpressure/signal schedules, TTY/jobs,
persistence/login, physical hardware and full UL-007/063/081/M3/R1 remain open.
No sibling policy implemented or whole-system acceptance inferred.

## Owned ABI24 composition consumed — 2026-10-03 (UL-007/012/081)

[Independent sys-init consumer](../docs/evidence/sysinit-session-consumer-2026-10-03/README.md)
verifies216 producer members/24 artifacts, reads back30 ISO modules and binds four
actual ELF/raw owners while preserving kernel/clients/entropy. Nine fresh local
replays pass (seven healthy/70reclaims and two exact pre-admission denials);15
semantic trace corruptions reject. No source rebuild or sibling/runtime changes.

Missing owned-entry dependency is closed. The original final-phase guest owner
failure remains unclassified; audit confirms host-accepted complete command input
and real fail-stop, not a guessed cause or fix. [Concrete diagnosis proposal](../docs/SYSINIT-SESSION-CONSUMPTION.md)
asks the owner to identify the first failing operation/state and qualify any fix
before maintained recipe/new lab promotion. SSDK-06 stays deferred; UL-007/063/081,
TTY/signals, package/storage/login, physical hardware and full M3/R1 remain open.

## Sys-init read-race checkpoint — 2026-10-04

UL-007/012/081: [independent repaired-owner consumption](../docs/evidence/sysinit-read-race-consumer-2026-10-04/README.md) verifies unchanged
kernel/client closure, actual old-owner EOF failure, repaired forced race and
live/error fail-closed controls. Matched sys-init developer kit is locally delivered;
full composition acceptance, maintained sys-init recipe, writeEPIPE qualification,
SSDK-06 reader and full M3/R1 remain open. Historical exact caller is unavailable.
No sibling implementation authority or release promotion is inferred.

## Maintained lab boot command — 2026-10-04 (UL-007/012)

[Fresh sealed-kit qualification](../docs/evidence/lab-boot-command-2026-10-04/README.md)
passes minimum/current Python admission/CLI/oracle controls and immediate/delayed
native boots using the unchanged repaired sys-init kit. Maintained boot.py owns
input selection, bounded capture and cleanup; no native ABI/grants/runtime change.
Sys-init candidate recipe, writeEPIPE/composition controls, general TTY/storage/
packages/hardware, independent reader and full M3/R1 remain open.

## Maintained owner recipe intake — 2026-10-04 (UL-007/012)

[Independent decision0185 consumption](../docs/evidence/sysinit-recipe-consumer-2026-10-04/README.md)
verifies full delivery/lock, minimum/current exact owner rebuild, actual ISO/ELF
closure and four pre-effect producer denials. Fresh source-rebuilt client/owner
kit passes immediate/delayed native workloads and20 terminal/reclaims. Maintained
owner recipe/build availability is closed in this bounded scope. Remaining
owner mismatch/exhaustion/Unknown-cleanup/composition, writeEPIPE, TTY/persistence/
packages/physical/full M3/R1 and independent reader remain open. One local adapter
pre-build failure is retained; no sibling code/grant/pin changes or new policy.

## Serial denial consumer checkpoint — 2026-10-04 (UL-007/012)

[Eight independent native denials](../docs/evidence/sysinit-denials-consumer-2026-10-04/README.md)
qualify five owner entry handle checks, actual console wrong-grant read/write and
halt denied after exact workload/ten terminals with console still held. Full
sealed source/artifact/ISO/ELF binding and38 corruption checks pass. No successful
halt/replay or inferred guest reclamation. Remaining finite exhaustion, uncertain
close/reclaim, full component-loader negatives, writeEPIPE, wider composition/TTY/
storage/packages/physical and full M3/R1 remain open; deferred reader unchanged.


## 2026-10-04 — UL-003/015/081 native SDK provider errors

Maintained native-musl recipe now checks realtime fallback and physical-page
sysinfo failures, preserving actual error/unchanged denied clock buffer. Fresh
source rebuild changes exactly two libc archive members. Three fresh native
cases plus private provider controls pass; candidate delivery and retained attempts
are [qualified](../docs/evidence/sdk-error-guards-2026-10-04/README.md).
No existing SDK pin or sibling changes. Aether independent consumption, real
native time/scoped-resource providers, other sysconf branches, broader overflow
and thread schedules remain open. New sys-init control deliveries can be consumed;
continued serial shell use still depends on explicit wider SESSION identity bounds.


## 2026-10-04 — UL-007/012/081 selected final controls consumed

Eleven native negatives independently qualify finite exhaustion, close/reclaim
denial, synthetic lost settlement, six exact loader negatives and actual writeEPIPE.
[Consumer evidence](../docs/evidence/sysinit-final-controls-consumer-2026-10-04/README.md)
verifies full packets/archives,72 modules/five owner bindings and81 mutations on
minimum/current Python. Wider loader/race/recovery/assembled review remains open.
Continued-use blocker: explicit Aether wider SESSION identity/lifetime contract
and delivery before matching runtime/bootstrap/PID/FD/pipe/wait and sys-init work.
Current epoch15/pipe9 bounds cannot be widened locally as a substitute.


## 2026-10-04 — UL-003/015/081 guard owner handoff closed in scope

Aether independently consumed the exact guarded SDK, three native cases and
ordered1349-occurrence archive comparison. [Local disposition](../docs/evidence/sdk-guards-disposition-2026-10-04/README.md)
verifies the full owner packet/archive,241 candidate inputs and actual raw traces.
Previous ar extraction covered distinct names, not duplicate occurrences; historical
bytes are preserved and stronger owner evidence is explicitly selected. No SDK
promotion or broad provider/reader acceptance. Wider SESSION delivery and actual
time/entropy/identity/resource/configuration contracts remain the next dependencies.


## 2026-10-05 — UL-003/015/081 explicit entropy and retirement consumers

[Entropy](../docs/evidence/native-entropy-consumer-2026-10-05/README.md): maintained opt-in explicit-grant C17 adapter/probe, five final
native cases and20 corruptions on minimum/current Python. Actual native denials,
quota/close/replacement and lying-adapter/kernel-quota controls pass; unsupported
ambient APIs stay unsupported. Initial ordering failure remains retained.
[TSD/retirement](../docs/evidence/native-service-retirement-consumer-2026-10-05/README.md): complete producer archive, six actual envelope bindings,
six final fresh VMs and30 mutations; binary replay is not a local source rebuild.
Initial successful nested-tool harness is retained and replaced by preflight-then-
owned-native groups. No production SDK/reader/assembly promotion. Full production
backend still needs blocked-creator/concurrent worker progress and actual provider,
identity/configuration/calibrated clock/resource acceptance. SESSION widening is
an independent missing Aether delivery; no local reset/widening workaround.


## 2026-10-05 — UL-003/015/081 blocked-primary consumer witness closes

[Worker reaper consumer](../docs/evidence/native-service-reaper-consumer-2026-10-05/README.md)
verifies full producer closure/eight payload bindings, replays eight fresh native
cases and rejects40 mutations on minimum/current Python. Real primary pthread_join
parks while a charged ordinary worker reaps81/one detached peers; exact native
authority/confirmed-stop/unmap/retire and accounting remain. This supersedes the
missing blocked-primary consumer witness above, not production SDK/concurrency.
Actual musl worker-origin/concurrent creation/dynamic cleanup, real providers/
identity/configuration/calibrated time/resources and measured engine lifecycle
remain owner work. Bare private origin support is already implemented; it is not
a matching wider SESSION profile. Continued ordinary shell use remains blocked
on the separate Aether SESSION lifetime delivery. Existing lab kit stays usable.


## 2026-10-05 — UL-003/015/081 worker-origin and clock consumers

[Origin consumer](../docs/evidence/native-service-origin-consumer-2026-10-05/README.md)
closes the selected actual-musl worker-origin/concurrent-preflight consumer gap:
ten fresh final VMs and50 corruptions on minimum/current Python, exact82/two
charged records,66/34-page mappings/2 allocator pages. Creation/cleanup phases
remain separate; dynamic overlapping creation/retirement/reuse and production
reaper placement/resources require further local/owner qualification. Fail-stop
primary/optional peer ordering finding and all attempts remain retained.
[Clock consumer/adapter](../docs/evidence/native-clock-consumer-2026-10-05/README.md)
qualifies11 producer binaries and three independently source-built explicit-grant
observe/park/sleep cases,81 corruptions each interpreter and host UBSan injected
return controls. q35 elapsed time now has consumer evidence; no UTC/physical
accuracy/effective resolution, wider workers, POSIX conditions or SDK promotion.
Next local UL-003/015 work: adapt actual musl timed waits with atomic mutex
release/reacquisition, original absolute deadlines and honest interruption/errors;
then sleep policy/providers/resource qualification. Keep old virtual waits/pins
and unsupported realtime honest. Kernel clock profile excludes service-workers;
matching expanded-clock owner costs/delivery is a separate prerequisite.
No UL completion beyond these selected witnesses. Wider SESSION profile/delivery,
M3/R1/release and SSDK-06 reader remain open; deferred review does not pause coding.


### UL-003/015/081 maintained service-runtime delivery — 2026-10-06

Userland now supplies the opt-in SDK supplement and maintained offline builder;
[exact delivery/qualification](../docs/evidence/native-service-runtime-2026-10-06/README.md)
records five final VMs, capacity/retirement/condition/long-wait/shutdown/exhaustion controls,
minimum/current builds and compact failures. These stories stay active.
Aether dependency: consume the sealed matching base+whole-archive supplement,
omit old conflicting adapters, initialize before actual engine threads and prove
engine/helper/ARC teardown before finish. Existing owner runner needs explicit
composition changes; --libc-build alone cannot silently supply the supplement.
Local follow-ons: broader interrupted/requeue/malformed
attributes and lifecycle schedules, independent technical/reader disposition,
public CLI presentation/documentation review before promotion. No new owner
acceptance or cross-project completion is inferred. Wider SESSION is separate.


### UL-003/015/081 actual OpenZFS waits consumer — 2026-10-06

[Four fresh source-built native cases](../docs/evidence/service-runtime-openzfs-consumer-2026-10-06/README.md)
pass normal, stop/replacement, disabled804 and early125;47 mutations rejected on
each minimum/current Python. Exact producer client/supervisor bytes, ISO readback,
actual CV/mutex map entries and owned cleanup verified. This supersedes pending
Aether SDK intake above. No initialized engine execution or UL completion.
Next dependency is Aether-owned whole provider composition/resource admission and
engine/helper/ARC startup/teardown, including identity/configuration/volume/UTC.
Wider SESSION remains separate. Broader runtime schedules, independent technical/
reader review and public SDK presentation remain local follow-ons before promotion.


### UL-003/015 shared UTC runtime handoff — 2026-10-06

[Maintained private UTC](../docs/evidence/native-utc-2026-10-06/README.md) consumes
new Aether raw RTC observations under explicit unauthenticated UTC policy. Four
final native cases,3040 host Gregorian comparisons, injected provider/UBSan,
minimum/current/standalone exact builds,50 corruptions and seven builder controls
per interpreter pass. Failure attempts retained; stories stay active.
Aether dependency now: exact314-member v2 UTC intake and checked actual engine
gethrestime/gethrestime_sec/getlrtime bodies, signed ns range and pool persistence.
Aether's current volume/file-vdev witnesses supersede earlier volume-unavailable
wording for those selected cases only. No engine/pool/service recovery acceptance.
Local follow-ons: broader worker schedules, profile-specific initial identity,
source trust/offset/drift/synchronization policy before production, reader/manual/
public CLI disposition and general POSIX. Wider SESSION remains independent.


### UL-003/015/081 UTC intake and isolated liveness — 2026-10-06

Aether independently consumed exact UTC-v2 and checked actual engine time bodies.
[Five focused runtime VMs](../docs/evidence/runtime-liveness-2026-10-06/README.md)
pass helper original-deadline conditions/reverse joins/TSD/32 detached cycles,
97/41 lifetime admissions, live0 finish and stop/replacement.63 trace corruptions
reject on both interpreters. No maintained runtime or sealed delivery changes.
The producer's first leap engine timeout remains unexplained; local schedules do
not reproduce that engine or close its gate. Next Aether telemetry/scheduling/
engine lifetime diagnosis; possible runtime attribution remains open. Do not widen
supervisor bounds or declare persistence based on later passes. Wider SESSION and
independent reader/owner disposition remain separate; stories stay active.


### UL-003/015/081 confirmed detached cycle correction — 2026-10-06

[Corrected elapsed v3](../docs/evidence/reaper-fix-2026-10-06/README.md) reproduces
old-v2 ordered cycle870 and qualifies stopped-owner cleanup without musl list lock.
Atomic free publication follows unmap/retire/live accounting; upstream creator/
join serialization, native authority and82/512/8192 bounds stay unchanged. Ten
native cases,115 trace corruptions per interpreter and minimum/current/standalone
archives pass. [Matching UTC v3](../docs/evidence/reaper-utc-2026-10-06/README.md)
passes six native cases,50+24 corruptions and eight builder controls per interpreter.
New294/343-member seals supersede immutable v2; maintained UTC builder rejects v2.
Next owner dependency: Aether exact new seals, ordered/serial detached exits,
lifecycle/exhaustion/stop and actual engine helper reuse before persistence. Earlier
engine timeout attribution remains unresolved; do not widen bounds or infer that
this witness diagnoses it. Broader interruption schedules, profile identity/source
trust, initialized persistent pool/transaction/reboot/service and independent
reader/owner review remain open. Wider SESSION is independent. Stories stay active.


### UL-003/015/081 corrected owner intake consumer — 2026-10-06

[Exact owner consumption](../docs/evidence/fixed-reaper-consumer-2026-10-06/README.md)
clears the known corrected-reaper delivery/intake blocker for elapsed/UTC v3.
15 retained final owner cases and three fresh local probes bind current captured
sources; native ELF/supervisor bytes match producer exactly. Eight-round overlap,
serial and511 detached retirements/512-denial per owner pass. Both interpreters
reject178 trace and five identity corruptions. Older failed exhaustion stays failed;
later moving owner engine/driver edits remain unqualified. Next owner gate is
actual SPA activation/physical ZIO success/error, then real pool under upstream
minimum and measured resources.8MiB raw-vdev remains a fixture. Earlier leap
engine timeout attribution, broad schedules/reader review, persistent transaction/
reboot/service, M3/R1 and wider SESSION remain open. Stories stay active.


### UL-003/015/081 empty SPA/root ZIO owner consumption — 2026-10-06

[Final activation triplet/ordinary UTC verification](../docs/evidence/spa-active-consumer-2026-10-06/README.md)
binds120 captured sources, unchanged6458 baseline, corrected UTC-v3, original
slot90 and57/49 origins. Eleven/eight checked rows, three owner generations/live0
and exact857/858 denials pass. Earlier solo positive/link/CLI failure history stays
separate. No fresh local native engine execution or compacted object/map rebuild.
Next Aether authoritative vdev allocation/open and physical completion/error/borrow
lifetime on sufficiently sized region;8MiB raw-vdev below64MiB minimum stays a
fixture. No pool/create/import/persistence/service or wider SESSION acceptance.
Original UTC timeout attribution and reader review open; UL stories stay active.


### UL-003/015/081 pool diagnostic review — 2026-10-07

[Host review/proposed owner patch](../docs/evidence/pool-diagnostic-review-2026-10-07/README.md)
binds the prepared nine runtime sites to maintained v3 and reproduces three
malformed/conflicting trace attribution gaps on both Python versions.36 valid
sites/16 existing denials pass; proposed patch preserves36 and rejects20.
Next Aether review/adoption and renewed diagnostic-run disposition following native
pool125/401/zero reclaims. Cause/retirement/persistence remain unknown; no retry,
quota increase or sibling edit here. Intervening physical storage evidence stays
owner-scoped; previous next-vdev wording is historical. Wider SESSION and reader
review remain separate; no runtime story or milestone closed.


### UL-003/015/081 full backing host consumer — 2026-10-07

[Prepared exact expression at32MiB](../docs/evidence/backing-scan-consumer-2026-10-07/README.md)
passes8192 clean pages/18 dirty boundary denials and detects two scan omissions.
Both interpreters reject70 corrupted/partial cleanup traces. Aether's creator pair
failed after second zeroing; importer never started. Next renewed native create-only
disposition for full verification, then matching readonly import if creator passes.
Host coverage does not attribute/repair the timeout. Earlier decoder proposal remains
pending and three gaps still reproduce, separate from this timeout. Native cleanup,
quiescence, persistence/M3/R1 and wider SESSION remain open; stories stay active.


## 2026-10-18 — operational Rust filesystem service

| ID | Status | Work | Dependencies / acceptance evidence |
| --- | --- | --- | --- |
| UL-082 | active | Implement Rust filesystem service policy and native engine/transport integration for persistent shell/runner/packages | Maintainer placement/source-bound producer handoff; experiments/filesystem-service/README.md and docs/evidence/filesystem-policy-2026-10-18/README.md. First private no_std policy:13 host tests/eight omission controls. Next lifetime-safe private C bridge, authenticated transport/reply-loss retirement and matching native engine consumer. Missing mutation/sustained engine qualification is Aether-owned; sys-init/pkg-mgr policy remains separate. No R1/M3/public API acceptance. |

UL-003/007/012/015 follow-ons: prior creator timeout/never-import wording is historical;
current Aether pair has one successful existing-file native overwrite/fresh readonly
readback. Independent full service/native acceptance is still required. Preserve
all earlier failures; do not infer sustained service or resources from that pair.
UL-082 keeps one nonempty provider call per context, conservative retirement after
committed/malformed/lost completion, no blind replay and coherent alias size.
UL-061/063 technical/reader migration remains; reader deferred, no coding stop.


### UL-082 C bridge/native object integration — 2026-10-18

[Maintained bridge/evidence](../docs/evidence/filesystem-bridge-2026-10-18/README.md)
qualifies host ABI/ownership/progress and native relocatable original-C/Rust binding,
not guest execution. Nine host tests, six lifetime/type, two ABI and omitted-write
controls pass; existing13 core tests/eight omissions remain separately qualified.
Next owner gate: [proposed matching selector](../docs/proposals/FS-SERVICE-NATIVE-ENTRY.md)
and renewed Aether disposition after its current repeated-write30s unknown outcome.
No retry or larger limits, no second write, no substitute oracle. Live authenticated
transport/reply loss, full metadata/mutations/resources and persistent runner/package/
sys-init composition remain; UL-082 active and M3/R1 open.


## UL-082 bounded transport checkpoint — 2026-10-19

Aether's current producer Rust-write/recovery and eight-write receipts clear the
historical callback/30s blocker. [Service transport evidence](../docs/evidence/filesystem-transport-2026-10-19/README.md)
adds a versioned bounded request loop, native entry/provisioning contract,
readiness, reply-loss/context retirement and endpoint cleanup.11 host tests,
four typed-C entry tests/seven omission controls and native object/ABI checks pass.
One nonempty Rust provider call remains; no observer/history reset or call-bound lift.
Next dependency: owner-selected writable+IPC engine/client profile (current actual
builder rejects this combination and only admits the old probe seal), full native
qualification and independent intake, then matched sys-init executable assembly.
[Concrete delivered proposal](../docs/proposals/FS-SERVICE-TRANSPORT.md); UL-082 active,
M3/R1 and launch/native enforcement/recovery remain incomplete. No sibling edits,
SDK/pin/old delivery changes, review approval or native service acceptance inferred.


### UL-082 next action — native handoff consumption, 2026-10-20

The [retained producer review](../docs/evidence/filesystem-native-consumption-2026-10-20/README.md)
clears the historical current-selector/timeout wait for the exact service artifact.
Next coordinate a matched Aether small-write retirement profile, then implement
safe repeated-context/provider lifetime in Rust. Existing retire accepts4096 bytes;
AFSRPC01 payload is16 and current profile has no retire hook. Keep one-write/context
until the matched contract/native witness exists. Preserve progress after close/
retire/reopen/reply errors and never replay unknown effects. Follow with service
namespace operations, idle/lifecycle delivery and matched sys-init/runner/packages/
Zsh acceptance. Userland owns policy; Aether owns producer/native qualification.


## UL-082 approved eight-write integration checkpoint — 2026-10-20

A separate27-member `filesystem-service-lifetimes-2026-10-20-v1` candidate now
implements the explicitly approved fixed eight16-byte scope. `check-service.py
--lifetimes` passes default and variant tests, compiling semantic omissions,
Clippy and x86-64 object/import/ABI checks. Per-call consume/check-retire/reopen
preserves aggregate attempt/outcome history and stops on post-write or reply
failure. Old25-member one-write delivery/default semantics remain unchanged.
Aether's exact matched native profile/negative/fresh-recovery matrix is in progress;
this remains build-only/host-qualified until that gate passes. Namespace operations,
blocking idle/lifecycle, exact executable/provisioning/readiness/shutdown and matched
init/runner/package/Zsh integration remain UL-082/M3/R1 acceptance work.


## Eight-write native producer gate passed — 2026-10-20

Aether's new exact27-member candidate/profile passes12 fresh guests with seven
images admitted before launch. Normal, partial-request and final-close-failure
complete eight16-byte calls with last795/fresh805; lost reply stops after one
788/fresh798 without replay. Full independent780248-byte final file/hash/metadata/
EOF, original ordered export/drains, all21 cleanup boundaries/three terminal0/
live0/reclaims3, recovered whole media/outside guards pass. Controller4096,
observer8192, writers60s6000/readers30s3000 and other bounds stay fixed. Sources/
tools frozen, all VMs joined/owned output removed.699-method Aether integration
checkpoint passes. Exact service reports are checked in-engine; retained numeric
observations are not a complete72-byte report or general failed-close proof.

Producer receipt: `../Aether/docs/evidence/fs-service-lifetimes-native-2026-10-20.json`,
SHA256 `cac88f4ff8faa4c86a4e2361d20ece087519008fa997687df3099e0ad6b54e4e`.
The retained old checker remains explicitly pinned to the old25-member receipt;
it does not verify this new result. This is producer evidence, not independent
userland native execution/human sign-off. Compact retention hashes repeated
unmodified dependency scans/source-context catalogues; no full archive/replay claim.
Old sealed candidate/default policy, SDKs and released standards pins stay unchanged.

The next UL-082 delivery must specify authenticated namespace mutation authority
and alias/POSIX rules, zero-staged mutation progress/retirement, idle/reply-loss
behavior and an exact executable/ABI/provisioning/readiness/shutdown contract.
Existing Aether `zpl-mutate.h` (bounded create/same-directory no-replace rename/
remove) and `zpl-resize.h` (bounded shrink) are private serialized engine-owner
interfaces, not client authority. Do not infer mutation permissions or silently
reuse16-byte retirement for zero-staged operations. Aether matches that new
candidate/profile; sys-init owns lifecycle and pkg-mgr installation. These gates
still block operational service/runner/packages/Zsh/ISO/M3/R1 assembly; finite
eight-call evidence is not general uptime or permission to reset history.


UL-082's2026-10-19 fixed mixed service profile now has matching7-image/12-guest
Aether producer qualification. Its bounded namespace/lifetime gap is closed for
that exact candidate. Operational executable/ABI/provisioning/idle/larger transfer/
readiness/shutdown and init/runner/packages/Zsh/ISO acceptance remain active; see
current STATE and the existing transport proposal. No story/milestone completion
or independent consumer acceptance is inferred.


UL-082 update2026-10-20: the separate49-member AF04 data gate has matching
7-image/12-guest producer evidence. The separately approved lifetime9/96 proposal
is next; see current STATE/transport proposal. Operational executable, directory/
metadata, activation and persistent runner/package/Zsh acceptance remain active.


## UL-082 checked lifetime producer qualification — 2026-10-20

The separate55-member AF04/ABI26 aether_fs_runtime_run candidate now passes
Aether's7-image/12-guest native9-mutation/96-request matrix. Complete796/806 recovers
p8192 in two independent blocks; lost/partial788/798 recovers empty p. Full original/
new file/metadata/namespace/media/export/drain/cleanup and5294 balanced primary
waits pass. All engine/controller pairs and six older seals stay exact. The only
subsequent code change is Aether's narrow page-fragment channel-copy fix, qualified
by actual-body/four compiling omission checks, full757 host checkpoint and four
legacy native channel guests. Writer60s6000/readers30s3000, authority/memory and
all other limits unchanged. Initial timeouts, monitor launch/retention errors and
host implementation failures remain; generated outputs are disposed.

Producer receipt: [Aether native result](../../docs/evidence/fs-service-runtime-channel-fixed-native-2026-10-20.json)
SHA256 695b1ee0a7bf537a6d42a976507dccce4b74ddd7fa83f7f799af4f5828c671a7.
This is finite producer evidence, not independent owner/reader acceptance or an
operational service. Keep UL-082/M3/R1 open. Next deliver the exact operational
executable/entry/resources/dependency/notice closure, authenticated block/dataset/
endpoint provisioning, generation-bound usable-namespace readiness and explicit
admission-close/drain/export/quiescence/reclaim contract. Sys-init's existing
persistent-boot intake requires those inputs before direct lifecycle wiring.
Preserve failed/uncertain outcomes; no reset/replay, new production service ABI
or shared PS adoption is inferred. Directories/layout/metadata/persistent loading,
runner/packages/Zsh/TTY and wider serial-session composition remain. No sys-init,
pkg-mgr or standards edit/message or SDK/released-pin change.


## UL-082 private activation preparation — 2026-10-20

Validated-root/UTC native readiness and exact retained live-instance consumer
checks are host-prepared, with ordering/error/no-replay and legacy coverage.
No activation delivery is sealed or native-qualified. Aether's actual 9/96
controller is 4,181 bytes versus the fixed 4,096-byte limit; the separate 8 KiB
proposal awaits a maintainer decision. See the existing transport proposal and
Aether's fs-activation-host/fit receipts. Operational executable/provisioning/
shutdown, directories/metadata, persistent program loading/packages/Zsh and
matching independent consumer acceptance remain; UL-082 stays active.


## UL-082 activation qualification and package-name capacity stop — 2026-10-20

Exact58-member activation producer passes7-image/12-fresh-guest recovery matrix;
[qualified final-byte/host review](../../docs/evidence/fs-activation-qualified-2026-10-20.json)
records the original EAGAIN assertion, bounded activation-only fixture repair,
semantic controls, unchanged old controllers and all output disposal. Owner source,
seals, released pins and current limits remain fixed. This is not independent
acceptance, operational executable or R1 completion.

Next package-path review identifies64-hex blob names versus the current16-byte
wire/mutation limit. The actual parser/policy rejects before effects. The separate
255/component510/rename proposal requires a maintainer decision; it reuses4096
scratch/framing, keeps all other workload/authority/memory/time/cleanup limits,
and changes no package format or sibling policy. Scope/tests/forbidden outcomes
are recorded in FS-SERVICE-TRANSPORT and Aether OPENZFS-FEASIBILITY. No code is
implemented without the decision. Operational entry/provisioning/shutdown,
directories/layout/metadata/loading/runner/packages/Zsh/sys-init remain.


## UL-082 approved AF05 component names — 2026-10-20

The maintainer approved255/component510/rename at unchanged other limits. Exact
61-member AF05 candidate is sealed; actual entry29/wrapper3/26 omission/strict ABI/
format/Clippy/object and legacy21/18 checks pass. Aether772 integration methods
and four controller fits pass. Native64-byte name recovery/interruption matrix
is next;255 native remains unrun. Keep old AF04/seals and all other limits fixed.
Operational service/directories/layout/metadata/loader/runner/packages/Zsh/sys-init
and independent acceptance remain; UL-082/M3/R1 stays open. STATE is authoritative.


## UL-082 AF05 package-length producer qualified — 2026-10-20

Exact61-member AF05 now passes Aether's7-image/12-fresh-guest matrix on64-byte
names differing at the last byte. Full796/806 recover8192 bytes; lost/partial
788/798 empty, no replay. Original/new file/metadata/namespace/EOF/media/export/
drain/all cleanup and5473 balanced waits pass. Old seals/pins and baseline/
independent controllers stay exact; frozen inputs pass and owned trees disposed.
[Native receipt](../../docs/evidence/fs-service-names-native-2026-10-20.json),
SHA25644125fdce33a0b06638e2a94e9ef281cfae768c0a3ab0c0ca48a83570353880d.
Entry29/wrapper3/26 omissions/legacy21/18/strict ABI and772 integration checks pass.
Every other resource/authority/workload/time/cleanup limit stays fixed. This is
producer evidence, not independent acceptance, operational executable or ISO.
Maximum255 is host/engine-contract coverage. The FFI still creates regular files
only and mutation policy is scoped to the provisioned root. Next operational
entry/resources/provisioning/shutdown and directory/hierarchy/layout/metadata/
loader/runner/package/Zsh/sys-init/TTY work remains; UL-082/M3/R1 stays open.
Do not reinterpret prior pending-native paragraphs as current STATE or lift any
bound from this result. No package-format workaround or RAM-only ISO.


## UL-082 delegated directory producer qualified — 2026-10-20

Exact67-member AF06 passes7 admitted images/12 fresh normal/lost/partial/close
and recovery guests, complete contents/hierarchy/metadata/ACL/inventory/media/
export/drain/cleanup,36 reclaims/live0 and2476 balanced waits. Old seals/pins and
all current limits preserved. STATE links compact results and guard-repair review.
Next is the explicitly approved separate storage lifetime profile, one120s test
with65s idle/post-idle I/O, at9/96 and unchanged other bounds. Operational owner/
provisioning/shutdown, metadata/cross-directory promotion, loader/runner/package/
Zsh/sys-init/TTY and independent acceptance remain; UL-082/M3/R1 stays open.

## UL-082 kernel idle-lifetime handoff — 2026-10-20

The separate AENBD005 owner27/engine26 profile now passes one120s writer with
6500 ticks idle, post-idle mutation/read4096 and fresh30s recovery.9/96 and other
bounds fixed, complete content/metadata/media/export/drain/reclaim pass; old seals
unchanged, outputs disposed. STATE owns the exact receipt/results. UL-082 stays
active: next exact operational entry/executable/resources, authenticated
provisioning and real failure/readiness/shutdown delivery, then matched consumers.
The finite C fixture is not that owner; no runtime/seal or release change here.


### UL-082 borrowed metadata input — 2026-10-21

Separate owner-only metadata.rs and the Aether native READ-only consuming gate
now pass. No AF06 wire/backend/default or old seal changed. STATE and the
filesystem-service README record exact scope and next metadata-capable handle/
reply delivery; ordinary mode/promotion and runner/package/Zsh assembly remain.
UL-082 stays active. No independent owner sign-off or R1 acceptance.


## UL-082 AF07 metadata service candidate — 2026-10-21

[New metadata service contract/evidence](../docs/proposals/FS-SERVICE-METADATA.md)
binds the original qualified getter to authenticated retained handles and explicit
METADATA16 attenuation under a separate AF07 wire.23 actual-entry host cases,
eight compiling omissions and strict C/Rust ABI/native-object/format/Clippy checks
pass on minimum/current Python; current AF06 entry/omission/regression checks also
pass. All old seals/executable and metadata.rs binding bytes remain unchanged.
Native service metadata selection/fit/negative/recovery, matching launch owner and
sys-init consumption remain incomplete; current Aether intake still selects AF06.
Old writable IPC gate is cleared, not the current blocker. No guest, pin/limit/
record reset or sibling implementation change. Ordinary mode/promotion, ABI29
shell/PID/FD, filesystem-backed runner/loader, packages/Zsh/TTY/ISO and R1 stay open.
UL-082 active; independent owner/reader review pending.


## UL-082 separate AF07 operational owner — 2026-10-21

Aether reports AF07's selected positive/failure matrices passing;875 current input
hashes match its latest approved provider receipt. The separate Rust AF07 owner
now selects the exact77-member service with metadata entry/rights31, preserving
old AF06 selection and lifecycle ABI. Eight actual-owner tests/nine compiling
omissions, five old-owner cases and native/C ABI/link/format/Clippy controls pass
on actual minimum/current Python. The new sealed object is not a linked executable.
[Next exact Aether link/intake/native gate](../docs/proposals/FS-AF07-OPERATIONAL-OWNER.md)
requires a separate AF07 build; current fs_launch.py hardcodes AF06 preparation/
owner/origins. Then sys-init consumes the matched executable/AF07 peer/readiness/
shutdown input. Native operational adoption/fit and independent review remain
incomplete; UL-082 active, M3/R1 and shell/loader/packages/Zsh/TTY/ISO remain open.
No extra guest, reused120s allowance, limit/reset/replay, old seal or sibling change.

## ABI29 client continuation — 2026-10-21 (UL-007/081/082)

The explicit [startup/identity candidate](../docs/proposals/SESSION-FS-ABI29.md)
passes host UBSan, nine semantic omissions, four native objects and eight legacy
object comparisons. Aether's operational AF07 gate is cleared with761 input
hashes matched. Source/object candidate is separate from native shell acceptance.
Next local work: complete matched CRT/libc/client/helper linking and resource fit,
then AF07 FD/path/immutable executable translation and selected shell workload.
Sys-init still owes matching parent1/child2–4 dispatch/FD/PID/wait and AF07
activation/shutdown input; do not modify siblings or reuse ABI24 artifacts by
relabeling. Required native witnesses and independent review remain incomplete;
finite SESSION limits, persistent packages/Zsh/TTY and M3/R1 stay open.

## Complete ABI29 linked input — 2026-10-21 (UL-007/081/082)

[Full client link/initial fit](../docs/evidence/session-abi29-link-2026-10-21/README.md)
closes the missing full CRT/libc/component/link input step, without closing native
shell acceptance. Explicit45/8 component inventories, minimum/current identical
ELFs, legacy whole-ELF regressions, mixed-link and sealed-recipe denials pass.
Initial73/24 pages fit128 including main stack; peak allocation/runtime fit stays
open. Next local work: AF07-backed FD/path and immutable filesystem executable
selection/loader requirements; matching sys-init ABI29 dispatcher and native
positive/negative/cleanup/fresh-boot witnesses remain external consuming inputs.
Keep finite SESSION lifetimes and all old seals. Packages, modes/promotion,
Zsh/TTY, reviews and M3/R1 remain open.

## Boot-parent consumer defect fixed — 2026-10-21 (UL-007/081/082)

[Corrected v2 client input](../docs/evidence/session-abi29-boot-parent-2026-10-21/README.md)
reproduces and fixes the actual generation0 supervisor/PID7 mismatch. The defect
is local and corrected; no kernel change or false parent needed. Strict host
regression/eleven semantic omissions, eight legacy object comparisons, equal
minimum/current linked clients and host parser/initial fit pass. Independent
consumer/native witnesses remain needed. Select v2; v1/object startup candidates
remain immutable but incompatible. Continue AF07 FD/path/immutable executable
translation and consume the next matching sys-init dispatcher/native input.
No finite lifetime/quota expansion or interim RAM-only shell substitutes for M3/R1.

## Read-only description core — 2026-10-21 (UL-007/081/082)

[Actual Owner-backed core](../docs/proposals/FS-DESCRIPTORS.md) supplies bounded
read/seek/dup/shared-offset/final-close/cloexec semantics without changing AF07.
Twelve host tests/eight compiling omissions pass; no wire/native/shell acceptance.
Next integrate trusted process FD admission and retained AF07 transport, preserving
one live Owner/SPA context, then real filesystem path/immutable executable loading
and matched supervisor/native lifecycle witnesses. The current core deliberately
reserves FD0–2, has no fork sharing/writes and rejects requested read ranges outside
signed64; it must not be advertised as a general POSIX FD or exec implementation.
Native resource fit, cleanup/persistence, packages/Zsh/TTY and reviews stay open.

## Read-only AF07 client — 2026-10-21 (UL-007/081/082)

Current sys-init decision0194 has consumed corrected ABI29 v2 and prepared
startup/child/wait core. Full dispatcher is pending our FD/path/immutable image
translation. [AF07 client](../docs/proposals/FS-AF07-CLIENT.md) now implements
lookup/read/stat/close/disconnect against existing wire, retaining checked tokens
and failing closed after unknown/malformed/partial I/O. Eleven host tests/eight
semantic omissions pass on actual minimum/current Python; no native runtime.
Next adapt shared descriptions to client transport without a second live Owner,
then exact process FD/directory/binding/exec contract and immutable-image policy
with sys-init/Aether. Do not treat raw read-only handles or hashes as executable
authority. Native assembly/fit/failed-exec/cleanup/fresh boot and M3/R1 stay open.

## Transport-backed file descriptions — 2026-10-21 (UL-007/081/082)

[AF07 shared descriptions](../docs/proposals/FS-REMOTE-DESCRIPTORS.md) now operate
over one dedicated fresh authenticated client; no local Owner/SPA. Common core
serves both current adapters. Host client/local/remote suites12/12/8 and controls
8/8/11 pass under both Python versions, with generic native libs only. No item
is closed by this host milestone. Next exact authenticated process FD/path/binding
messages and fork/lifetime/failed-exec preservation, immutable executable admission,
matching sys-init full dispatcher/fit/shutdown and Aether native qualification.
Readonly file bytes alone cannot stand in for executable trust/immutability.

## Process-view file policy — 2026-10-21 (UL-007/081/082)

[Process views](../docs/proposals/FS-PROCESS-DESCRIPTORS.md) now share13 descriptions
across shell1/children2–4 with exact stored keys, sequential generation history,
per-view flags and all-view final-close scanning. Native authenticated admission/
copy/settlement remain dispatcher obligations; no new wire or grant.18 process
host tests/eight omissions and local/remote regressions pass on both interpreters;
canonical startup source reused/pinned, no native runtime. Next exact process FD/
path/binding messages and immutable executable/failed-exec/native-copy contract,
then full dispatcher/fit/shutdown and Aether native witnesses. Never call local
commit/settled hooks to replace missing/unknown native evidence. M3/R1 remain open.

## File RPC messages — 2026-10-21 (UL-007/081/082)

[AEFD0001](../docs/proposals/FS-FD-WIRE.md) now supplies exact open/read/seek/dup/
close/flags messages and actual C/Rust codecs over authenticated-caller-selected
process views. Every opcode checks current key; no payload identity is authority.
Caller-owned workspace/pending reply guard handles bounded framing and lost reply
without replay.9 host tests/eight omissions plus process18/eight pass on both
interpreters; C17/UBSan and generic native libraries only. Select v3, preserve
superseded v1 and corrected-runtime v2. No native acceptance or story closure.
Next new C facade profile and dispatcher startup/FD/console/pipe bindings, exact
native copy/failed-exec/immutable executable contract, resource placement/fit and
native cleanup/fresh boot. Old shell wire is not silently switched; shared greeting
has exactly one consumer. Native workspace/state cannot be assumed to fit4088 stack.


2026-10-21 UL-007/081/082 continuation: C file-client transport is host-qualified
([contract](../docs/proposals/FS-FD-CLIENT.md),1631 schedules/seven controls on both
interpreters). Full libc facade/FD routing/startup/pipe/console selection remains
active; use matching owner-reviewed input, not silent ABI29 replacement. Native
endpoint binding/deadlines/fit, copy/failed-exec parent/FD preservation, immutable
exec authorization and sys-init dispatcher/native acceptance remain follow-ons.


2026-10-21 UL-007/081/082: typed file facade is host-qualified through live C/Rust
pipe exchange (74 cases/six omissions on both interpreters). [Contract](../docs/proposals/FS-FD-FACADE.md).
Remaining: consuming shell startup/FD routing across file/pipe/console without
conflicting ownership; native copy/failed-exec parent/FD preservation, immutable
exec admission and complete fit/dispatcher/native qualification. No full libc
selection or POSIX/UL/M3/R1 closure is implied.


2026-10-21 UL-007/081/082: [AEFDT001 tagged startup candidate](../docs/proposals/FS-FD-BINDINGS.md)
host decoder/lookup passes65951 cases/five omissions on both interpreters. Owner
reconciliation remains required; implement explicit shell startup/table replacement
and console/pipe/file dispatch/mutations using actual source rights/lifetimes.
Do not infer type from overlapping integer selectors, duplicate live ledgers,
select unaccepted snapshot or claim native authority from validated shape. Native
copy/failed-exec/immutable admission and whole fit/dispatcher acceptance remain.


2026-10-21 UL-007/081/082: tagged read dispatch now host-qualified through actual
file C/Rust exchange and synthetic stream completion modes ([contract](../docs/proposals/FS-FD-ROUTING.md)).
Next reconcile/select complete shell startup/table and actual stream adapter;
implement open/close/dup/flags/pipe mutations coherently without duplicate ledgers.
Do not treat synthetic stream tests, a read seam or proposed startup as native
rights/lifecycle/fit acceptance. Native copy/failed-exec/immutable exec and matched
dispatcher/commands/errors/cleanup/fresh boot remain follow-ons.


2026-10-21 UL-007/081/082: [one-table file operations](../docs/proposals/FS-FD-TABLE.md)
now qualify logical open/dup/seek/close/cloexec with source-confirmed publication
and failure preservation (269 live host cases/six omissions on both interpreters).
Remaining: owner-reconciled explicit shell startup/profile/table and actual stream
adapter/mutations, native copy/failed-exec preservation, immutable image authority,
complete fit and matched dispatcher/native command/error/cleanup/fresh boot. Unknown
open/dup can have remote effects; never treat preserved local map as rollback.


2026-10-21 UL-007/081/082: [mixed stream aliases and observed final close](../docs/proposals/FS-FD-STREAMS.md)
now host-qualified:14 pipe/completion scenarios per child,269 live file cases/six
controls on both interpreters. Same canonical map; consumed-error and unknown
outcomes distinguished, file3/pipe3 isolated. Remaining: owner-reconciled actual
native console/pipe adapters, pipe creation/write and selected shell startup/table;
native copy/failed-exec preservation, immutable image authority and full fit/
dispatcher/native command/error/cleanup/fresh boot. Local cloexec flags do not
implement native exec enforcement; unknown close requires owner reconciliation.


2026-10-21 UL-007/081/082: [tagged output](../docs/proposals/FS-FD-WRITE.md) now
qualifies short/full/zero output, known-error continuation, unknown with actual
bytes/no bytes, class isolation and fail-stop/no replay on host.18 output+14
predecessor stream scenarios per child/269 live file cases/six omissions on both
interpreters. Remaining: actual native stream adapters, pipe creation, selected
shell/startup/table and owner reconciliation; native copy/failed-exec preservation,
immutable image authority and complete dispatcher/fit/native acceptance. Unknown
output is not zero effect. No file writes or native readiness implied.


2026-10-21 UL-007/081/082: [paired pipe helper](../docs/proposals/FS-FD-PIPE.md)
now preflights two logical slots, validates a complete unused ordered source pair
and publishes together.22 host creation scenarios plus unchanged18 output/14
lifetime scenarios per child,269 live file cases/six omissions on both interpreters.
Actual OS pipe transfer/alias/final close is separate from injected completion
and native capability truth. Next actual native adapters, coherent shell/startup/
table and exact redirection; copy/failed-exec preservation, immutable image authority,
whole fit/matched dispatcher/native acceptance. Unknown source allocation may exist;
never infer rollback or close conflicting purported selectors. UL/M3/R1 remain open.


2026-10-21 UL-007/081/082: [stream chosen-target replacement](../docs/proposals/FS-FD-REPLACE.md)
is host-qualified (19 scenarios+unchanged22 creation/18 output/14 lifetime per
child,269 live file cases/six controls on both interpreters). Self preserves flags;
distinct success resets target flag. Consumed close error leaves hole; unknown
preserves metadata/retired admission. FILE crossings reject -38 until actual
source-backed replacement exists. Next full redirection, native adapters and
coherent shell/startup/table selection, owner/reader reconciliation; copy/failed
exec/immutable image authority and whole fit/matched dispatcher/native acceptance.
Do not expose this subset as atomic POSIX dup2 or treat preserved map as rollback.


2026-10-21 UL-007/081/082 descriptor batch: [integrated session](../docs/proposals/FS-FD-SESSION.md)
now groups fresh startup/operations/flags/seek/inert export/terminal finish with one
borrowed map/client.15 integrated+73 predecessor scenarios per child,269 live file
cases/eight controls on both interpreters; eight x86-64 objects/relocatable link and
41 static frame reports (maximum264) are build evidence only. Shutdown reports
known leftovers/unknown/raw transport errors and caches receipt without replay;
projection validates before filtering and never closes or authorizes exec. Sys-init
0198 now consumes prior mixed helpers on host, so those are no longer missing.
Next full source-backed FILE replacement, authenticated native adapters/coherent
linked shell/startup, owner/reader and native copy/immutable/failed-exec/whole-fit/
matched dispatcher/native acceptance. Do not treat local receipt as native cleanup.


2026-10-21 UL-007/081/082 [file/stream redirect batch](../docs/proposals/FS-FD-REDIRECT.md):
prepared source duplicate, chosen-target close/publication and actual rollback
cleanup now qualified together through session+real unchanged Rust service.482
live cases+88 prior host scenarios per child/eight controls on both interpreters;
192 partial reply headers cover all three phases. FILE replacement is no longer
wholly missing. Limits: remote spare descriptor required, consumed target error
can leave hole, unknown/unpublished allocation needs owner reconciliation; no atomic
POSIX dup2 promise. Next authenticated native adapters/linked-shell/startup and
immutable image/copy/failed-exec/full fit/matched dispatcher/native acceptance.
