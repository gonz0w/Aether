# AF07 client endpoint preparation — 2026-10-21

[Decision0195](../../decisions/0195-af07-endpoint-adapter.md) and
[adapter guide](../../../prototypes/native-filesystem-session/AF07-TRANSPORT.md)
record scope. Host execution uses the actual sealed Client/Framed with typed
kernel doubles; native preparation emits/disassembles real ABI29 trap methods.
No guest/trap execution, linked full dispatcher or code/stack/heap fit is claimed.

preparation.json binds all5 client/77 service members, sources, exact tools,
commands/logs, native object and host test binary hashes. It rechecks dependency
bytes, existing startup/core/serial/AF06/AF07 sources and tools after tests. No
producer-supplied build/test scripts run; copied pinned Rust library sources are
compiled by explicit local commands. Six tests exercise actual framing/client
retirement through every partial greeting/disconnect prefix, both wait directions,
wait exhaustion/error, old version/invalid rights/stale reply, returned close
errors, no replay and both endpoints closed exactly once despite failure.

Three compiling omissions select one real test each and fail semantically:
wrong wait direction, missing second close and missing cached-close guard.
Native disassembly retains int0x81 with24001/24002 selection,24004 wait and24003
close, with unused arguments zero. Native calls remain unexecuted; host tests do
not prove kernel holder enforcement, native scheduling or cleanup. Existing
panic=abort profile is used; unwinding Kernel implementations are not qualified.

prior-attempt1 preserves the first passing host/build/lint logs followed by an
omission-generator selector failure: it expected pre-rustfmt wait spelling.
Corrected selector targets the formatted call; runtime source did not change.
The rerun completes all three compiling controls. This is not a native retry.
Source copies and preparation-driver.txt retain the exact final procedure.

local-checks.json records full local checks; sha256.json seals all packet files
except itself. Full dispatcher integration remains blocked on userland's shared
FD/path/binding and immutable executable contract. Local handoff is unsent.
All accepted owner/default/release pins and sibling files remain unchanged.

A follow-up native input-closure check pins the three Rust core/builtins/alloc
rlibs against the existing immutable tool manifest before/after five explicit
native builds. All five outputs reproduce byte-for-byte; original logs and the
new library-closure command logs remain distinct. Host toolchain/library-wide
reproducibility and native runtime acceptance are not inferred.
