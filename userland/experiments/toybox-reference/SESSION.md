# Shared write/finalization state (UL-067)

The host-only [session wrapper](session.c) composes unchanged [vector](VECTOR.md)
and [finalizer](FINALIZER.md) components. It shares the vector poison state with
all shutdown callbacks. No Toybox/libc/native code is wired; CAT-06 stays NOT RUN.

A private zeroed ts_state owns the two component states. Callers use ts_write and
ts_finish exclusively, with the same valid/disjoint borrowed-object requirements
as the component APIs. Logical roles are not native FD assignments or grants.
Callbacks can reenter the session APIs but must not otherwise mutate its fields.
This is synchronous code; no thread or asynchronous signal safety is claimed.

If finalization begins with poisoned transport, all three local roles are consumed
and marked abandoned without close or diagnostic callbacks. Preserve a prior
nonzero command status; otherwise return1. This records local loss of usability,
not remote release. If finalization is called inside an active write callback,
it also poisons that in-flight result and abandons the roles. The outer write
cannot report known success even if bytes were committed remotely.

On a healthy connection, delegate ordering/status logic to the tested finalizer.
Unknown or malformed close/diagnostic returns poison the same session state.
Known failures remain distinct from uncertainty. Public writes are rejected once
finalization starts, including callback re-entry; finalizer's bounded diagnostic
callback owns any authorized last diagnostic delivery. The caller must forward
its actual write/command failure status; the wrapper does not invent or recover
an earlier known error supplied as status0.

Completed finalization returns the stored result without more effects. Invalid
startup preconditions transfer no role ownership; caller retains cleanup duty.
The flushed flag remains a caller precondition, not a witness of real flushing.
Callback success does not prove native reclaim, rights or lifecycle accounting.

## Tests and reproduction

```sh
python3 -B experiments/toybox-reference/check-session.py
```

From repo root, pinned Clang21.1.8/Python3.12+, no VM/network/SDK required. Strict
C17 warnings, UBSan, pinned format and owned60-second command bounds apply. The
driver records source/plan/tool hashes and private outputs. Help/version stdout0,
invalid usage stderr64. All consumed component bytes are preserved unchanged.

[Evidence](../../docs/evidence/toybox-session-2026-09-06/summary.json) records4,096
combinations of initial write outcomes, three close outcomes, diagnostic outcomes,
prior status and shutdown callback re-entry. Independent event transcripts verify
no callbacks after uncertainty, original status, initial abandonment, stderr-last
ordering and no post-finish writes. Four boundary checks include finish-during-write,
invalid flush acknowledgement and null APIs. Three compiled mutants drop initial
poison handling, lose close poison or permit writes after finish; all are rejected.

This exercises host callbacks, not musl plus finalization in one executable or any
native transport. Earlier Linux musl-loop evidence remains separately scoped.
Independent review and actual child roles/admission, stdio patching, shutdown hooks
and reclaim remain pending. Next local work: implement/test the proposed bounded
process-mask state, including initialization, save/restore and process isolation,
without replacing native umask until the startup contract is accepted.
