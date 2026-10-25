# Command-I/O consumer review and handoff (UL-056)

Userland's real bytecount source and host controls are prepared under
experiments/command-runner. Aether's NATIVE-COMMAND-IO is now a concrete local
integration candidate; at this checkpoint no completed command-runner producer
bundle was present in docs/evidence. The immutable older file-I/O receipt cannot
stand in for this new broker/adapter. Native execution waits for an exact completed
candidate source archive, report and terminal expectations, not for new kernel
capacity. No sibling file was edited or owner approval recorded by this review.

## Consumer interpretation of the candidate

Use its separately selected command-runner mode on ABI 9. The broker owns two
records and positions: immutable input, distinct output scratch. Parent bindings
are 3/read and 4/read-write; child bindings 0/read and 1/write. Bootstrap is one
32-byte response; validate status, both nonzero/distinct references, exact indices/
rights, and reserved word before publishing either local entry. Publish all or none.
No backend handle, offset or copied parent pointer belongs in the client table.
The eventual command adapter must provide initialized bounded TLS separately from
the transport-free bytecount source and finish bootstrap before entering its main.

Launch is the candidate's fixed 384-byte frame, not an invented protocol:
32-byte header (op 4, version, argc/envc, two entries, zeros), padded command name,
two 32-byte inheritance entries and eight padded startup strings. Copy 1–4 argv
and 0–4 env strings under the candidate bounds and LC_ALL=C allowlist. Treat every
byte as data. Keep exact destination order 0/read then 1/write. Unknown name,
invalid source, rights widening, duplicate destination, malformed/padded strings,
unsupported counts and flags must reject before effects. Every launch header,
including malformed ones, consumes the full declared fixed frame; test a valid
request after rejection to prove framing alignment. Partial-frame EOF is a failed
workload, never accepted admission or an operation to replay automatically.

Collection is a 32-byte frame (op 5, receipt, zeros), separate from both file
bindings. Retain observed terminal detail/kind and consume once. Parent file close
must not erase the child result. A successful delivery followed by source-buffer
mutation tests copied startup; it does not prove safety under arbitrary concurrent
memory mutation. Native rollback retains its finite channel-generation costs.

## Output verification finding

The current owner helper closes parent input, collects child exit, then reads EOF
on FD 4. Because that alias shares the output position advanced by the child,
ordinary reads cannot retrieve `6\n` from the beginning. Exact output bytes and
input preservation are currently verified by the broker through its backend
handles. The candidate prose's claim that the runner checks output should be
qualified accordingly; this review does not modify that owner's document.

For bounded independent adoption, retain this trusted owner verification explicitly
and exercise a skip-write/wrong-output control that it must reject. Do not call the
runner's EOF observation an independent byte comparison. Full CR-01 acceptance
must either retain a clearly designated service-side verifier with its own evidence
or add an agreed independent output-observation operation/record; client-only seek
or position reset would violate the shared-position contract. This is a concrete
review issue for the owner, not an invented byte layout or automatic approval gate.

## Native consumer work (UL-057)

After a completed matching producer exists, build an independent aether-run client
and two-binding adapter alongside the prepared bytecount source. Keep native
bootstrap separate from command logic, use actual musl read/write/close, and reuse
whole-connection poison/no replay rather than the owner candidate's implementation
without review. Preserve old consumer/source pins.

Required initial cases: nonempty and empty input with identical command bytes;
actual argv/env; immutable command selection; malformed/incomplete framing;
duplicate destination, rights and source rejection; real reservation/admission
rollback; short output and output-full refusal; normal/nonzero/fault distinction;
consuming collection; parent-close/child survival; final backend/native cleanup;
and byte readback through its explicitly named enforcing/verifying layer.
Record omitted full-CR-01 gates rather than relabelling a finite suite complete.
Package reconstruction and sys-init lifecycle composition remain separate owners.

The prepared command uses 0/1/64 status values under Experience. A runner may map
its own admission/selection errors as proposed, but must preserve actual command
nonzero status and native terminal kind. Host --help/--version support does not
mean a 64-byte native output file can hold every help response; that case should
report real capacity failure if tested. A larger buffer or diagnostic channel
requires its own workload, not a hidden quota change.

The current candidate intentionally exposes no open/seek/dup, general FD range,
PATH, shell grammar, pipes, fork/vfork/exec or TTYs. CR-01 is a useful spawn-only
command tier, not dash/M3. Shared normative decisions and PD owner reviews remain
in Aether-standards. This local review is not approval on behalf of other projects.

## Subsequent producer and consumer completion

The producer subsequently published the completed native-command-io bundle.
UL-057 verified it and completed [nine independent native cases](../experiments/command-runner/NATIVE.md).
The earlier absence note is historical. Owner byte verification versus runner EOF
remains explicit; public CLI and full-CR-01 gates stay open.
