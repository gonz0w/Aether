# Local source store — host fixture v1

OR-03 implements byte storage only. Original work: SPDX-License-Identifier: BSD-2-Clause.
Use `sh tools/source-store.sh --help`. This uses POSIX sh and the existing Python
host-tooling dependency (standard library only), because descriptor-relative opens,
no-follow checks and atomic no-replace publication are not safely expressible in
portable shell. This is not a target runtime decision. Tested host/tool identities
and actual results belong to [OR-03 evidence](../evidence/or-03/PLAN.md).

## Commands and bounds

| Command | Inputs and successful effect |
| --- | --- |
| init ROOT | Creates a previously nonexistent directory, mode 0700, with marker `.origins-store`, `objects` and `tmp`; never adopts an existing directory |
| put ROOT SHA256 SIZE INPUT | Copies and verifies input into private temporary storage; atomically links complete bytes into `objects/SHA256` without replacement; identical retry verifies existing bytes |
| verify ROOT SHA256 SIZE | Rehashes the complete stored file and checks size; no mutation |
| get ROOT SHA256 SIZE | Verifies into a private temporary snapshot before writing raw bytes to stdout; removes only its successful attempt's temporary name |

All paths must be absolute printable ASCII, at most 4096 bytes, with components
1..255 bytes; empty/dot/dot-dot components and symlink traversal reject. On macOS
use the physical `/private/tmp` path, not its `/tmp` symlink. Parent directories must
already exist. Store directories must be owned by the effective UID and mode 0700.
Ancestors must be stable and trusted. The marker is exactly `origins-private-store-v1`
plus LF; it is a format marker, not an ownership or cryptographic credential.

SHA256 is exactly 64 lowercase hex characters. SIZE is canonical unsigned decimal,
0..16,777,216 bytes inclusive, a deliberately smaller fixture budget than the 1 GiB
record proposal. Input files must be regular and have one link. Reads are streamed
in chunks at most 64 KiB; at most expected size plus one byte is read before a size
rejection. No metadata/recipe code is run and no archive is extracted. Objects use
a flat digest directory; sharding from the storage design is deferred.

Stored objects must be regular files. Multiple links are permitted there because
an interrupted publication can retain a second name in `tmp`; exact bytes are always
reverified. Malicious same-UID/root writers, external hardlinks created by such
writers, ancestor renaming and compromised storage are outside this private fixture
boundary. Owner control is an assumption, not sandbox enforcement. Directory opens
are descriptor-relative and no-follow; FIFO opens are nonblocking then rejected.

Success for init/put/verify is `[OK] COMMAND: ESCAPED_ROOT` on stdout. This is human
output; do not parse it as an authentication protocol. Get stdout contains payload
bytes only and should be redirected to a private file, not displayed as terminal
text. Diagnostics are plain ASCII status rows on stderr with `ORIGINS-` identifiers;
paths/errors are escaped. `--help` and `--version` exit 0. No prompts or color modes.

Exit 0 means the described byte operation succeeded; 2 means a format, identity,
limit or policy precondition rejected; 1 means I/O failed; 64 means usage error.
Ctrl-C exits 130; other signals retain OS termination behavior. Missing Python exits
2 with TOOL-UNAVAILABLE. Symlink open errors/missing files are IO-ERROR, distinct from
TYPE-INVALID after opening a nonregular file. Generic I/O failure is not evidence of
an identity rejection. No exit status grants authenticity or execution authority.

## Interruption and recovery

Publication uses same-filesystem hard linking with no replacement. Before that link,
failed puts leave no new object. After it, interruption can leave a complete object
without a success response. Retry the same pinned identity: it rechecks the complete
input and existing object. Concurrent identical writers can both succeed; a changed
existing object is rejected and never repaired/overwritten. Output permissions are
0400, not administrator-resistant immutability. No fsync/power-loss durability is
claimed. Required unsupported filesystem operations fail without fallback.

Each put/get owns a fresh exclusive `tmp/attempt-*` file. Ordinary failure, killed
processes and failed cleanup can retain partial or complete attempts. Never resume
or trust their names as admitted objects. Successful attempts remove only their own
temporary link. An init failure can leave a partial root; it is not automatically
adopted or deleted. Use a new private root for another initialization attempt.

After a failed operation, retain the error, expected identity and directory evidence.
Verify any final object before retrying. Corrupted objects require a separate inspected
recovery decision/new store, never an overwrite flag. A maintainer may inspect and
remove explicitly owned abandoned scratch after preserving needed evidence and
ensuring no operation is using it; this command has no prune/delete feature.
Interrupted get can leave partial stdout after verification; callers must check exit
status and publish their own output only on success. It never emits corrupt input
before verification. Full storage/publish failures preserve prior objects and may
retain temporary bytes. Total retained scratch has no automatic quota/GC; operators
must bound the disposable filesystem and invocation count. This is not a service.

See the [test plan](../evidence/or-03/PLAN.md) for oracles and exclusions. Publication,
TUF, extraction, pkg-mgr handoff, native execution and independent review remain
separate work. No external package has been admitted by this fixture.
