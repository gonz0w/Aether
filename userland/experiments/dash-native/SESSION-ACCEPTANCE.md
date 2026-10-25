# Current composed SESSION acceptance

2026-09-25: **SESSION-01–06 accepted for the private scripted profile**. All910
native cases pass:121 capacity,358 connections and431 command-runner. Eight
independent SESSION comparisons,14 prior lifecycle comparisons and25 checker
rejection controls pass;115 Python and configured Zig/Rust host checks also pass.

This record tracks the unchanged [proposal](SESSION.md) and
[composed script](session/composed.sh). The proposal and its manifest retain their
original NOT RUN fields because their bytes are pinned producer inputs. This record
supplies current scoped acceptance after the matching regression completed.

| ID | Native observation already checked | Acceptance |
| --- | --- | --- |
| SESSION-01 | Actual dash main executes the complete script in each of three parent lifetimes; exact65-byte stdout and19-byte stderr, all positive terminal statuses zero | Accepted, private007/ABI21 |
| SESSION-02 | Both three-stage pipelines use actual copied builtin writers and two helper replacements; child statuses, EOF and terminal groups precede observation and reuse | Accepted, private007/ABI21 |
| SESSION-03 | Actual helper substitution returns argv output, dash removes its newline, and x remains correct after the next pipeline | Accepted, private007/ABI21 |
| SESSION-04 | Final helper finds fd3–63 closed; exact separate stderr and resumed stdout match the consumer files | Accepted, private007/ABI21 |
| SESSION-05 | Eight live cases exercise exact output, wrong environment, substitution corruption, leaked descriptor, stale wait and retained-writer outcomes | Accepted, private007/ABI21 |
| SESSION-06 | Three complete parent generations,27 copies,21 helper execs,24 image admissions and30 terminal records/reclaims; exact generations and cleanup ordering | Accepted, private007/ABI21 |

## Independent controls

| Case | Required result observed |
| --- | --- |
| composed | Three full successful sessions with exact streams and30 reclaims |
| wrong-env | Helper91, parent31, supervisor2800,2 reclaims, empty streams |
| bad-byte | First pipeline says Pipe data; normal30-reclaim completion, ordinary exact-output checker rejects |
| bad-substitution | Parent33, supervisor2801,6 reclaims; only argv and first pipeline on stdout |
| fd-leak | Helper95, parent35, supervisor2802,10 reclaims; final success output absent |
| stale-wait | Collected child identity returns ECHILD without changing status; entire session still succeeds |
| stale-accept | Deliberate stale acceptance yields parent144, supervisor2803 and5 reclaims; only the documented pipeline prefix race is allowed |
| retained-writer | Real parent fd10 write alias blocks EOF with pending reads/wait; three confirmed stops, supervisor2804 and5 reclaims |

The observation operation is owner-only, bounded and hex-framed, and rejects
emission before worker/channel cleanup. Each positive parent's exact terminal
identity group precedes its observation. Twenty-four mutated traces additionally
reject wrong admission identity, duplicate observation and observation before
cleanup; the real bad-byte case separately exercises the ordinary stream oracle.

## Evidence and remaining scope

[Independent consumer evidence](../../docs/evidence/session-consumer-2026-09-25/README.md)
binds the sealed producer export, tools, SDK, source review, separate raw streams,
owned-process cleanup and linked owner stack audits. One collector selector error
was corrected with both versions and the failed attempt retained; native results
were not changed or rerun to accommodate it.

This is private AENMX007/ABI21 scripted execution. The existing twelve-script
component matrix remains12/12 across separately qualified fixtures. Full UL-007/M3
and R1 remain open. Next compose early-reader recovery followed by another command,
failed-exec recovery, scratch redirection and real serial input. Each requires a
new explicit workload and owner delivery; current script/helper pins stay unchanged.
UL-081 shared SDK work, independent source/reader reviews, general signals/TTY,
persistence, package execution and sys-init assembly remain separate requirements.


The first follow-on [recovery workload](SESSION-RECOVERY.md) is now pinned with
passing syntax/static checks. RECOVERY-01–06 is NOT RUN natively; owner delivery
and independent replay remain required. The accepted SESSION inputs are unchanged.
