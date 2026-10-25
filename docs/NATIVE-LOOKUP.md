# Bounded executable namespace lookup

2026-09-05. Rust user-space conformance experiment over unchanged
[AENEX001 / native launch v1](NATIVE-LAUNCH.md). No new kernel operation, envelope,
bootstrap grant, file protocol or shared standard. The unreleased canonical
[process/descriptor proposal](../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md)
remains subject to its owner review; this is not POSIX exec or namespace adoption.

## Contract

A trusted launch owner binds the two boot-supplied executable grants to immutable
relative names `helper-a` and `helper-b`. A Namespace borrows an explicit immutable
entry slice; lookup searches only that slice. The conformance fixture also supplies
a restricted slice containing only helper-a and an empty slice. There is no
fallback to a wider namespace, PATH, cwd, numeric grant parsing or host files.
These names are fixture identifiers, not a proposed distribution directory layout.

Names contain 1–31 ASCII letters/digits or `-_.`; exact `.` and `..`, slashes,
NUL, whitespace and non-ASCII bytes are invalid (negative EINVAL 22). Overlength
is ENAMETOOLONG 36, missing name is ENOENT 2, and a matching entry without an
executable binding is EACCES 13. Length validation precedes content validation.
No normalization, symlinks, traversal, mutable entry replacement or allocation.
The static fixture table has two unique entries; it is trusted bootstrap data,
not an untrusted manifest parser. File-read permission is not executable authority.

Successful lookup returns an existing owner-bound executable grant. The named
launch wrapper resolves before invoking the existing native launch operation;
lookup failure does not admit a child or consume a slot generation. Subsequent
kernel launch errors retain their documented semantics. Actual launch still
requires the caller's factory/executable bindings and a valid copied startup
record. argv[0] and the selected name remain separate values.

A Namespace is **user-space policy, not a kernel capability or isolation boundary
against its own process**. Code in the trusted launch owner can bypass this helper
and invoke any native grant it already owns. Passing this mapping to an untrusted
process would not transfer kernel grants. A future process service must bind its
requester's namespace using authenticated IPC authority; this fixture supplies
no such service or cross-process lookup protocol. The kernel continues rejecting
workers that guess factory/executable values.

## Target witness

```sh
python3 scripts/launch_smoke.py --lookup \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
```

This reuses the two strict-musl helpers and launch conformance client with a
separate Rust build configuration. It exercises restricted/empty lookup, invalid
and missing names, missing executable binding, rejected named launches followed
by first-generation admission, correct selection of both ELFs, copied startup
bytes, denied worker launch, retained results, reclaim and replacement/fault.
The marker stays `AETHER NATIVE LAUNCH PASS`; the receipt identifies `lookup`.

Seven cases: positive; wrong second ELF (child 92 / supervisor 411); malformed
machine, reserved envelope and invalid loader layout; a widened-namespace policy
control (supervisor 431 before admission); and a wrong name-to-grant binding
(child slot 0 status 92 / supervisor 411). Only exact rejection contexts pass.
Source/tool/libc pins, commands, maps, small artifacts and serial identities are
retained as in the launch runner. This validates the lookup/launch seam, not file
content loading, shebang interpretation, fork, in-place exec, inherited descriptors,
parent wait/reap, a native shell or package installation. Those are later work.
