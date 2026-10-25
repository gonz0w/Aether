# Public musl fork pipeline — 2026-09-15

The pipeline parent now calls public fork for all three children. The verified
musl1.2.6 source archive supplies fork/_Fork and private headers; the staging
substitution and existing REBIND_LIBC_REPAIR helper match the earlier public-fork
candidate. The helper rebinds auxv and channel caches after native copy; upstream
_Fork repairs child TID registration/cache before returning. The native owner still
observes the source freeze and stages both pipes before copying.

Children check gettid/getpid, new memory/channel auxv, denied old parent channel
authority, CLOEXEC metadata and private TLS/stack state. They then exec into the
existing seven-binding libc replacement. Parent identity/private values survive
all three calls. Three generations require nine public forks, nine replacements,
exact ten-byte data and EOF on both pipes and fifteen normal reclaims.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes all25 native cases on276 frozen inputs. Target cases total
66.916 seconds. The no-child-repair mutant omits __post_Fork on the
child path and must produce child115 then owner2607 with zero reclaims; timeout
or unrelated panic is not accepted. Existing23 cases retain their exact meanings.
There were no failed attempts. All intentional rejection logs are preserved.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0; host.log records104 passing host checks. Final checks bind pinned Rust/C
formatting, workflow/standards/experience, simplicity manifest/four members,
whitespace and final source verification. Full matching connections/runner and
independent SDK/userland intake remain separate gates; unchanged shared adapter
and rebind code keep their preceding legacy qualification.

## Provenance, compatibility and limits

fork_source_sha256 matches the pinned SDK receipt. fork_inputs hashes original
extracted headers/sources/COPYRIGHT; archived build outputs preserve transformed
syscall headers, exact _Fork staging substitution, no-repair control and compiled
objects. Upstream diagnostics retain the existing candidate scope; first-party
clients use Wall/Wextra/Werror. No new dependency version, public API or published
SDK change is introduced. The original rebind source is unchanged.

compatibility.json compares 29 old top-level ELF/raw images; 29 are byte-identical.
Existing owner12424 fits16384; native slot/channel/page/generation limits remain.
No kernel, shared descriptor adapter, SDK, sibling repository or released pin
changes. The new staging header has explicit register outputs and memory effects;
stack buffers remain valid/private across copy. Upstream copyright is preserved.

This is a private public-fork candidate with fixed fixture snapshots and owner-
driven exec, not unchanged dash pipeline acceptance. Consumer-driven tables,
dynamic pipe/fork/close/wait orchestration, SIGPIPE, additional interruptions,
matching full suites and independent intake remain open. Persistence/packages/
sys-init assembly remain R1 work; no full-shell or release claim follows.

The preimplementation review is in NATIVE-SHELL-STARTUP. Runtime and review-input
archives preserve source and local guidance/test support. Target reports bind
commands, tools/SDK, timestamps, envelopes/ISOs and serial hashes. collect.py
verifies every generated file against its archive before removing only this run's
private output root; cleanup.json records it. Prior sealed evidence is unchanged.
SHA256SUMS covers this packet except itself.
