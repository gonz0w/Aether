# AF07 descriptor input intake — 2026-10-21 / BG-067

The new five-member userland descriptor source candidate and its unchanged77-
member AF07 dependency verify exactly. [The input record](AF07-DESCRIPTOR-INTAKE.json)
binds all hashes and applicable clauses, existing coverage, compatibility limits
and missing work. This is a source/contract review; no producer commands, compile,
new host tests or guest were run. Source-only delivery does not clear the bridge gate.

The candidate implements owner-local read-only descriptions: file FDs3–15,13
fixed records, shared offset/final-close for aliases, independent opens, read4096,
checked seek, per-FD close-on-exec and fail-closed retirement. Root LOOKUP|READ
attenuates to file READ. Userland reports12 real-Owner host tests/eight compiling
omissions with synthetic storage; Aether independently ran12. Those remain
attributed host evidence, not sys-init execution or actual OpenZFS/native transport.

The crucial compatibility boundary is ownership. `Descriptors::new` takes a
whole dedicated `Owner` by value and attaches one trusted peer. Retirement calls
`owner.shutdown()`. It cannot take over or duplicate the operational service's
live Owner/SPA. Local alias offsets do not implement cross-process fork sharing;
local Drop/detach is not endpoint closure/export/quiescence/reclaim. Calling
`commit_exec_close` before confirmed image admission would destroy failed-exec
state. Unknown exec cannot safely commit or restore by replay.

The smallest useful next change is userland's operational bridge/client contract,
not a new sys-init filesystem owner or speculative wire format. Request, locally
and unsent: authenticated process/instance/FD routing to the one live AF07 context,
exact bounded directory/lookup/open/read/seek/close/binding messages, rights and
generation checks, partial/error/unknown semantics, final disconnect obligations,
and immutable executable/loader translation preserving parent/FD state on failed
or uncertain exec. No fake RAM directory, PID-as-authority or second Owner/SPA.

Sys-init retains responsibility for full startup/descriptor/copy/exec/wait/endpoint
transport and AF07 shutdown composition, code/stack/heap fit and actual owner
handoff after that contract arrives. Aether then qualifies the matched assembled
artifacts and native command/error/cleanup/fresh-readback witnesses. The existing
startup/child-wait core remains prepared; it is not a linked full dispatcher.
Persistent packages, Zsh/TTY and assembled ISO remain open. No new generic service
framework, runtime dependency, standards exception or release/default pin change.

Applicable O/I/E and Distribution RL clauses preserve sole ownership, explicit
unsupported behavior, bounded state/failure, exact inputs and claim layers. No
new runtime behavior is adopted. Old serial/AF06/AF07/v2 artifacts and retained
reviews remain unchanged. This intake replaces no historical evidence or owner
review, and claims no independent release/reader sign-off.

Sources: [userland contract](../../../userland/docs/proposals/FS-DESCRIPTORS.md),
[producer evidence](../../../userland/docs/evidence/filesystem-descriptors-2026-10-21/README.md)
and [Aether consumer intake](../../../docs/evidence/fs-af07-policy-core-intake-2026-10-21.json).
Exact source/dependency bytes are pinned in the local input record; sibling results
are attributed evidence, never automatic runtime/build inputs. BG-067 retains
all missing operational bridge/dispatcher/native work; no new question ID needed.
