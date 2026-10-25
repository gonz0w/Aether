# Serial external substitution review — 2026-09-13

Requirement: connect the qualified native external substitution path to actual
serial dash. Run two `/next` substitutions in one shell, then a clean replacement
shell. Each child must survive denied exec, retain its pipe writer through actual
replacement, produce five bytes, close descriptors, and reach real wait/ack and
reclamation. Preserve independent child, pipe and source-copy generations.

Forbidden: stale pipe generation accepted at commit or replacement startup;
CLOEXEC aliases surviving successful exec; prior child state reused for a later
child; false EOF, early prompt, missing terminal, leaked resources or ambient
executable/console authority. Rejection controls corrupt only the second cycle.

Owner/profile: Aether private connections owner and C fixture, existing bounded
UART backend. Userland owns the eventual SDK consumer; no sibling changes or
acceptance claims. Kernel ABI, capacities, released pins and upstream bytes stay
unchanged. No new dependency, unsafe boundary, service or concurrency mechanism.
Existing synchronous frozen-child publication and channel buffer lifetimes apply.

Simplicity: composing the existing serial and exec paths is the simpler choice;
a second launcher or general shell framework is unnecessary. Two per-child flags
are reset on admission and checked before wait acknowledgement. No obsolete path
is removed because existing profiles retain regression value. General pipelines,
interrupted exec recovery and distribution assembly remain outside this change.

Selection: host tests and workflow/pin checks, focused positive and two semantic
rejections, then complete connections suite including older serial and exec
profiles. Freeze runtime/test inputs during runs; retain every failed attempt.
Check C/Rust formatting and old client ELF compatibility. Update STATE and native
console/shell/connections references with measured results and remaining limits.

Status: bounded producer qualification passes. The focused three-case run passed
on its first attempt (38.85s), followed by all280 connections cases in
855.59s. Host tests (100 Python tests plus Zig/standards checks), scoped C/Rust
formatting, workflow and the separately pinned simplicity snapshot pass. No
runtime/test source changed during either target run. No failed target attempt.

The packet retains251 frozen sources, the harness's237 source hashes,
4986 final target artifacts and910 focused artifacts, with member-by-member
archive hash verification. `qualification.json`, `native-traces.json`, command
receipts and full serial exchanges carry exact results. `implementation.diff`
is relative to the prior native-exec packet; sealed prior evidence is untouched.
See [the contract](../../NATIVE-SHELL-STARTUP.md#serial-external-substitution--2026-09-13)
for replay via the existing connections command and its pinned SDK/tool lock.

## Scope and next acceptance target

The serial owner is15,384bytes; controls are15,400 and15,416, all within16,384.
All92 older copied-fork client ELFs and the previous pipe writer ELF are unchanged;
267 older owner images are unchanged and only the three native pipe-exec variants
change. The new serial role is appended, preserving older image indices.

The next workloads are the unchanged userland DASH-argv and DASH-signal-table
scripts, captured read-only in next-consumer-inputs.json. They are not run or
accepted by this packet. Preserve their actual helper, arguments/environment and
trap/substitution semantics when qualifying a consumable adapter. The present
fixture still admits only the boot-granted `/next` writer and deliberately probes
`/denied`; it does not resolve arbitrary executable paths from a filesystem.

Documentation collection initially found no console-reference member in the prior
packet. The retained failure record and links.json identify the explicit
append-only console comparison; other documentation uses the prior sealed snapshot.
This did not change or rerun runtime inputs.
