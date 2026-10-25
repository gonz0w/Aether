# ABI29 filesystem activation candidate

This is the first sys-init-owned activation slice for Aether's separate
AENFS003 profile: engine0, process slots1–5, owner6. It leaves the existing ABI24
serial candidate and all developer/standards locks unchanged. See
[decision0190](../../docs/decisions/0190-filesystem-init-owner.md).

The entry validates all six bootstrap values, allocates the two reserved d002
channels, transfers the engine endpoints, delegates the scoped block region and
requires live generation-bound readiness plus the AF06 root greeting. It admits
one selected small `p` process at slot1 using program0xc002. After that dependent's
normal exit0 and confirmed reclaim, it sends one clean disconnect, validates the
reply, requires engine normal exit0, EOF/EPIPE, closes remaining endpoints, reclaims
the engine, closes console authority and requests quiescent halt. A returned halt
or any failure traps; unresolved resources are retained, never replayed/restarted.
The exact pinned engine's clean status is an aggregate shutdown claim, not proof
of media persistence, pool/device quiescence or every lifecycle phase by itself.

Only pool metadata changes through import/export; file contents are not modified.
The dependent is the producer's small process image, not
a filesystem-backed shell or runner. Init does not include the producer's fixed
nine-mutation transcript. Aether has now executed this exact owner natively,
with exported-file readback
and five fixed failed peers. The [local consumer review](../../docs/decisions/0191-filesystem-native-consumption.md)
records identities, independent failure-span checks and positive-tail limits.
This is not a usable persistent shell, general service manager or R1 image.

## Reproduce local preparation

Use the existing `docs/aether-session.lock.json` Rust1.98.0 compiler identity and
the installed x86_64-unknown-none target. No SDK download or sibling source is
needed to compile this owner. From the repository root, choose a new private
output directory. With `rustc` resolving to that exact compiler:

```
mkdir out/my-filesystem-owner
rustc --edition=2024 --test -Dwarnings prototypes/native-filesystem/policy.rs -o out/my-filesystem-owner/tests
out/my-filesystem-owner/tests
rustc --edition=2024 --target=x86_64-unknown-none -Dwarnings -C opt-level=s -C panic=abort -C relocation-model=static -C lto=fat -C codegen-units=1 -C jump-tables=no -C link-arg=-Tprototypes/native-filesystem/owner.ld prototypes/native-filesystem/init.rs -o out/my-filesystem-owner/owner.elf
rustc --edition=2024 --target=x86_64-unknown-none -Dwarnings -C opt-level=s -C panic=abort -C relocation-model=static -C lto=fat -C codegen-units=1 -C jump-tables=no -C link-arg=-Tprototypes/native-filesystem/owner.ld -C link-arg=--oformat=binary prototypes/native-filesystem/init.rs -o out/my-filesystem-owner/owner.raw
```

On this macOS host the pinned compiler may need its adjacent `lib` directory in
DYLD_LIBRARY_PATH. Scope that environment to compiler/rustfmt/Clippy only; passing
it to LLVM disassembly caused a retained preparation failure. Default Clippy and
rustfmt are checked separately. Local tests execute the actual policy with typed
doubles; they do not exercise native capability enforcement or the trap wrapper.

The sealed [preparation evidence](../../docs/evidence/filesystem-init-owner-2026-10-20/README.md)
retains exact commands, source/tool identities, host cases, omission controls,
ELF/raw and scoped stack inspection. Aether's private read-only
`fs_init_intake.py` command accepts both explicit hashes and never runs the owner.
That external inspector is not an implicit dependency of the owner build.

## Native integration handoff

The delivery binds the30-member filesystem manifest
`b69fd748b4d4fda334126dba96744a73f2a4b03649d5e9b1033ae253d52cc558`
and filesystem ELF
`89bbc3291a3d13d3639503048f6378a2ffac351d1cfe689d698135cbeab24997`.
It targets the already defined ABI29/block-in-rdx bootstrap; no other envelope
or role mapping is supported. The old15-lifetime SESSION bound is unchanged.

Aether's explicit `scripts/fs_session.py --sys-init-checks --run` now consumes this
exact delivery and reports eight fresh passing guests. The [consumer review](../../docs/evidence/filesystem-native-consumer-2026-10-20/README.md)
closes the old missing assembly gate for the first bounded activation. Native
sources and preparation hashes remain unchanged. The retained candidate JSON
still describes its original preparation layer; no default lock is promoted.

Local checks independently validate the five complete retained kernel failure
spans and the sealed reported positive disposition. Positive UART tails omit early
admissions/cleanup, so complete positive-trace replay is not claimed. An exported
pool's metadata may change even when original file bytes remain unchanged. Future
native behavior changes require fresh matching consuming witnesses and complete
records appropriate to their claims; these old results cannot qualify them.

The next [persistent boot handoff](../../docs/FILESYSTEM-BOOT-HANDOFF.md) needs a
matching ABI29 shell/client dispatch/PID/FD closure and filesystem-backed runner/
package inputs. The small `p` image supplies neither. Wider SESSION lifetimes and
userland's shell/TTY resource fit remain separate; the current limit is fifteen.
Aether's current R1 handoff names Zsh/TTY; sys-init selects no shell language here.
The default ABI24 recipe, old pins and released standards stay unchanged.
