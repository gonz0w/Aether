# Path-enabled owner and immutable read probe —2026-10-23

[Pre-code contract/security/simplicity review](../../../../sys-init/docs/decisions/0221-root-path-owner.md).
[Earlier root-path client](../filesystem-root-paths-2026-10-23/README.md) and
[exact protocol interoperability](../filesystem-path-wire-2026-10-23/README.md)
remain scoped evidence, not full native/Zsh acceptance.

[Build results](build-results.json) retain exact commands, source/tool/dependency
hashes, compiling controls and measured full owner. Selected producer38 tests/15
controls, C1010 fork-stage scenarios/nine controls plus exec/readiness and78 actual
libc binding cases, owner56 host methods/controls, ten fixed-helper complete/error/
short-operation outcomes and real initialized-TLS shell/helper parsers pass.
Old same-wire byte differential is default-only; native-input rebuild runs default
producer37/default owner57 including that differential. Separate versions instead
require actual C/Rust/C and opposite-version tests. No pass is inferred from a
compiler failure or omitted suite. Only current Python executed; minimum3.10
runner unavailable. Implementation-agent technical review; independent review pending.

Two initial C test-mock failures remain failed in [attempt1](attempt1.json) and
[attempt2](attempt2.json): four-byte item assumption, then redundant inspection
of an already-cleared mock request. Exact paths are checked inside synchronous
reply; complete request clearing stays unchanged. Production codec/libc did not
change to satisfy these mock fixes. All children stopped before owned outputs
were removed; no retained test trees, sources or binary/image archive.

[Fresh inputs](fresh-inputs.json) bind the default enginev12/activationv8/guardedv7
and separate path/probe guardedv8 to actual current sources. Default owner39376
code; selected40640/49152 code,7504/8192 resident and8000/8184 conservative stack.
Shell/helper use80/33 pages within existing128-page partitions. The exact native
[prepared sequence](../../../../docs/evidence/af07-root-read-2026-10-23/README.md)
awaits fresh disposition; no new guest ran. Default component API/pins stay exact.

The new private libc bridge supports canonical root-relative/absolute reads only,
with old defaults preserved. It adds no CWD or mutable system-root access. Writable
home requires real separate subtree authority, per maintainer policy. Public dup2,
writes/stable persistent executable loading, package/Zsh/TTY/ISO remain open.
