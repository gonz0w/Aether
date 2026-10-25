# ABI29 process views over AF07 — UL-007/081/082

Current follow-on: [authoritative file view v1](FS-FILE-VIEW.md) supplies the
read-only presence/cloexec input requested by sys-init0202/BG-071. The selected
owner gate/frames exist; exact enforcing comparison and full native composition
remain consumer work. Existing evidence and candidates are unchanged.

The additive [serialized copy v1](FS-SERIALIZED-COPY.md) now holds exclusive
file-ledger access across a native-copy callback and local inheritance. The old
inherited_child frozen-parent contract remains unchanged; matching owner
admission/wire/child transition and native qualification remain open.

Current maintained source adds validate_binding(key), a pure call to the existing
exact-key check used by every [AEFD0001 opcode](FS-FD-WIRE.md). The18 process tests/
eight controls rerun on both Python versions. The original15-member candidate and
evidence remain immutable; the new FD-wire candidate carries the additive entry.
No native authentication or old wire semantics change.

`ProcessFiles` in `experiments/filesystem-service/process-descriptors.rs` adds
trusted central-broker process views to the shared descriptor implementation.
It holds one AF07 client,13 shared descriptions and four13-FD views for existing
shell1/children2–4. Engine0/spare5/owner6 never become file-caller roles. No second
Owner/SPA, new service grant/opcode, native quota/lifetime change or process
admission occurs. This private Rust candidate supplies local inheritance and
instance binding rules; it is not a shell protocol or native fork/exec service.

[Evidence](../evidence/filesystem-process-fds-2026-10-21/README.md) qualifies host
policy/interoperability with actual sealed AF07 service/Owner and synthetic
storage. Sys-init's decision0195 endpoint adapter and its subsequent remote-
description compatibility are companion results, not executed again here.
The complete decision0194 startup packet is verified; its exact BSD-2-Clause
startup.rs is pinned/copied for canonical identity checks, not recreated.

## Trusted integration API

All identity/admission/settlement calls belong to the trusted dispatcher. It must
already own the exact native instance and authenticated channel/observations.
A request's PID, handle, FD or frame fields cannot call these admission hooks or
select its process authority. Canonical numbers validate labels only. Future
message dispatch must resolve the actual endpoint to its stored current key.

`ProcessFiles::connect(channel, service_epoch)` owns a fresh dedicated AF07 client
with matching externally enforced LOOKUP|READ delegation. Invalid provisioning
returns both local close results. `NativeIdentity` reexports sys-init's exact
slot/epoch/handle/PID/memory structure. It is checked, not treated as a grant.
Opaque `Process` keys retain exact full identity and service epoch; membership
compares that full stored key. Service epochs must not be reused.

| Trusted operation | Preconditions/effects |
| --- | --- |
| admitted_shell(identity, observed_parent) | After native admission on actual channel. Exact shell1, generation1–3, boot parent7, canonical handle/PID/memory via pinned greeting validator. All old process views must be settled. Generation starts1 and advances exactly once without reset. Publishes an empty shell view. |
| inherited_child(parent_key, child_identity, observed_parent) | After confirmed native copy, with parent frozen across native copy/local binding setup. Parent is current shell1; child is slot2–4, exact canonical identity, actual parent equals shell PID. Child slot must be empty and its next generation1–15. Copies bindings and flags atomically locally; shares retained descriptions/offsets with no lookup/new grant. Native rejection must not invoke it; failed setup/native cleanup stays caller-owned. |
| current(observed_identity) | Resolve trusted authenticated native observation to already registered exact key. No admission, caller authentication or repair of mismatched fields. |
| open_read/read/position/seek/duplicate/close | Exact current key and view first; then existing bounded AF07-backed semantics. Cross-view aliases share offset/final-close lifetime. Independent opens retain separate descriptions. Wrong process/FD/range produces no source request; reads initialize output before identity validation. |
| set_close_on_exec / commit_exec_close | Flags are copied on inheritance, independent afterward. Commit removes flags in that one view only, preserving other processes' aliases. Destructive local step AFTER actual image admission; no loader/staging/failed-exec implementation. |
| settled(key) | ONLY after actual exact native instance and endpoint settlement. Remove this view's aliases; close source handle only after last alias across ALL views. Keep generation history. Any close error retires source/table and retains occupied process ledger; it must not be reported as native reclaim/settlement success. |
| abort | Retire all descriptor admission and local endpoint obligations with no wire disconnect/replay. Preserve process ledger occupancy as unresolved; no fake native settlement. |
| disconnect | Only with every process view settled. Busy returns without consuming live table/client. Otherwise acknowledge AF07 disconnect, record both local closes, close future admission. Ok([-9,-5]) is failed cleanup after acknowledged disconnect. |

Parent settlement can remove its view while child aliases remain valid; replacement
shell admission waits for all children. Late keys/observations cannot select a
replacement view. No child-of-child fork, arbitrary role, skipped/reused generation
or generation reset is silently supported. Slots/generations remain existing
bounds; four-view memory is source-only preparation and needs native resource fit.

Shared `Descriptions<S, VIEWS=1>` specializes existing local/remote APIs to one
view. ProcessFiles privately uses four. Only binding arrays multiply; the global
13-description/AF07-handle budget stays fixed. Last-close scans every view; copy
needs no new backend handle and can inherit a full table. FD0–2 remain outside
this file-only core. Existing public single-view entry points delegate to the
same indexed algorithm; no duplicate read/seek/lifetime implementation is added.

## Failure and execution boundaries

Canonical identity/parent errors preserve sys-init's local negative error code;
other local outcomes distinguish Stale, Busy, Generation and Files(original
Failure::Source or local descriptor failure). These are private Rust values,
not POSIX errno translation or a new machine message contract. Existing AF07
responses and all old shell/startup frames remain unchanged.

Known open/read errors preserve current offset/aliases/flags. Tests exercise a
missing open with unchanged parent/child state; that is NOT failed native exec.
Failed/unknown exec must not call commit_exec_close or publish replacement native
identity without the agreed owner contract. Readonly handles, cached size or
digests never freeze mutable bytes or authorize executable admission.

Fatal I/O/protocol/close errors retire the shared source and every view. Process
records stay occupied if settlement did not complete; no automatic replay, reset,
reconnect or new shell follows. Endpoint closes are separate from native process/
memory/holder cleanup, service context teardown, engine export/device quiescence
and halt. The dispatcher must retain and settle those external obligations.

No native endpoint authentication, copy/admit/terminal/wait/reclaim, console FDs,
full pathname/cwd/symlink resolver, shell FD/binding messages, mutable operations,
image staging/loader/immutable trust, package or supervisor policy is implemented.
The current sys-init child/wait ledger remains its separate native-lifecycle owner;
this file ledger does not replace it. Exact process/path/exec messages and atomic
native-copy/exec admission contracts still require composition/review.

## Qualification and consumption

```
python3 -B experiments/filesystem-service/check-process-descriptors.py
python3 -B experiments/filesystem-service/check-descriptors.py
python3 -B experiments/filesystem-service/check-remote-descriptors.py
```

Actual Python3.10.21/3.14.7 pass18 process-profile tests (eight existing remote,
eight new process-view and two unchanged imported startup tests), eight process
semantic omissions, plus local12/eight and default remote8/eleven regressions.
Strict Rust1.98/2021 warnings/unsafe denial, default Clippy/rustfmt and native
no_std generic-library builds pass. Per-suite native bytes match both interpreter
runs. Unchanged client12/eight prior qualification is reused with exact sources,
not rerun. No native monomorphized runtime link/stack/heap/IPC or shell execution.

Process controls omit inherited bindings, cross-view last-close retention, exact
service epoch/instance membership, sequential child generation/history, all-view
shell admission barrier or per-view flag update. Test sources, commands, raw logs,
tools/pins and all failed/incomplete attempts are retained; no warning suppression.

Source-only delivery:
`build/service-deliveries/filesystem-process-fds-2026-10-21-v1`. It includes current
common/adapters/client/tests, process fixture and pinned identity/provenance, with
license/contract/dependency record. Earlier ten-/five-/77-member candidate bytes,
SDK/released pins and accepted native owners are unchanged. Independent technical/
reader and affected-owner integration review remain pending.

Next: exact authenticated shell process/FD/binding/path messages and failed-exec/
immutable executable admission; sys-init full dispatcher/readiness/shutdown and
concrete resource fit; Aether matched native command/error/cleanup/fresh-boot
witnesses. Packages/Zsh/TTY, general POSIX and full UL-007/081/082/M3/R1 stay open.
