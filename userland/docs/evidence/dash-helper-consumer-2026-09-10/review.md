# UL-007 consolidated command intake — pre-execution review

Select immutable shell-helper-child-2026-09-09, manifest SHA256
92b0c1abf626679479343614c25daf1a85af412b6041229bd3a791802366f971.
All 29 entries verified before selection. Compare to the independent 401-case
backend consumer. Frozen changed sources and source diffs are in review-inputs/.
No sibling implementation changes; original imported dash objects and separate
ENV-enabled main stay pinned. Helper bytes must match the local BSD-2-Clause
reference. Retain upstream notices, generated objects and previous evidence.

Scope and review: reproduce all 431 original command cases plus all six connections
cases because transfer_bounded is shared. It keeps generic 100000 attempts, uses
4096 for command backend exchanges, checks progress bounds and partial EOF, and
returns failure on exhaustion. This is an attempt bound, not a latency guarantee.
Silent/late and zero/16-byte EOF fixtures poison the client without replay or
publishing unknown state. A late witness closes request delivery, observes one
byte, leaves the rest unread and requires scoped confirmed stop before retirement.
Existing omission controls must reject with zero native reclaims, not time out.

ENV cases invoke actual dash main: equal IDs load hello.sh; UID/GID mismatch,
noninteractive, absent and empty ENV suppress loading. The old unguarded main is
used only for deliberate mismatch controls. Unsupported -p and unchanged syntax
script require exact diagnostics/status 2. There is no set-ID or TTY claim.
The helper uses existing explicit image authority, four arguments and two allowed
environment strings. The unchanged helper checks spaced argument, literal star
and WITNESS, writes eight bytes, and the wrapper closes inherited descriptors.
Mutations of argv/env return 91; skipped body and omitted closes must reject.
Parent private TLS and consuming child collection stay checked. Path/UID names
confer no authority. This does not qualify dash fork/exec/waitpid or DASH-argv.

Tests/oracles selected before execution: full original case order and statuses,
all previous 41 independent final serial checks, all 30 added cases with exact
terminal/supervisor/panic arrays; original guest/owner assertions check stream
bytes, non-publication, masks, live descriptions and confirmed native stop.
Compare final completed receipt digests only. Preserve failures and all serial/
QEMU logs. Check owner images within unchanged 8192-byte bound. Native command
budget 1800 seconds, connections 300 seconds, original per-guest 30-second watchdog
and native tick guard unchanged. Each output stream is bounded at 512 MiB; the
existing owned process runner records controlled PATH/LC_ALL/private TMPDIR,
exit and complete host cleanup. Native zero-reclaim mutants are not recovery.

Use existing pinned Clang/LLVM, Rust wrapper, Zig, QEMU and 4311-file SDK receipt;
verify before use and source/SDK after each suite. Exact flags/ABI/artifacts are
in the original native receipts. Host syntax runs on actual Python 3.14.7; no
minimum-version, fresh SDK, host-kernel or M4 claim. No kernel/build changes select
M4; changed shared transfer does select connections. Run local quality inventory
and whitespace checks before completion. No runtime behavior is changed locally.

Applicable O-01–05, I-01–06, E-01–08; local Distribution NC/PX/TR/OB and approved
quality TD/TC/TE, CE/CD/CP and documentation evidence apply within this experiment.
Technical assessment by the executing assistant is scoped intake review, not
independent security or reader signoff. UL-016/061–063/081 remain open.

Simplicity: the simpler alternative is the existing explicit launcher, chosen
for the present helper boundary rather than adding a second process mechanism.
Consolidate the already sealed sequence into one regression run. Remove no
compatibility paths or immutable evidence; the process implementation remains
an owner dependency. Polling generalization is narrow but shared, hence six
connection regressions. Full M3 remains incomplete regardless of this result.

Actual results: pending. Any failure stays retained and blocks its claim.

## Actual disposition

All 431 command and six connection cases pass locally; 71 independent final serial
checks pass, including every new case. One local attempt, no source/oracle change
or retry. Both commands exit 0 and record complete host process cleanup. All 551
source and 4311 SDK hashes remain unchanged. New owner maximum 8152/8192 bytes.
Unchanged helper/syntax input identities were checked separately. Original producer
failures and intermediate source snapshots remain retained. No independent reviewer
or reader approval is inferred from the executing assistant's assessment.

Documentation impact: update current UL-007 backlog, STATE, ROADMAP, gap record,
WORKLOADS and METADATA with these bounded observations. Add evidence to the existing
draft coverage entry. Preserve earlier dated snapshots and all immutable evidence.
Next separate intake: verified public-wait packet (147 connections/five launch),
including its source-built public fork/wait candidate. Not locally executed here;
non-normal wait, reply failures, wait4/wait3 and exec remain owner/integration work.

Final verification: local quality inventory check passed; source-audit/reader/
publication gates remain separate. Executed driver, SDK receipt and both native
receipts match recorded hashes. Retained drivers compile on Python 3.14.7.
Changed tracked documentation passes `git diff --check`. See [verification](verification.json)
and [quality output](quality.log). SHA256SUMS binds the retained packet bytes.
