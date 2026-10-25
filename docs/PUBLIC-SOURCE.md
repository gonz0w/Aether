# Public source boundary

The owner selected a clean public snapshot of the reviewed Aether consolidation
on 2026-10-25. The kernel, userland, sys-init and pkg-mgr source share this repository.
Unaccepted AF09 changes, private Git history, generated bundles, SDK copies and
companion repositories remain local. Compact historical summaries describe only
the experiments they originally recorded; excluded receipts are unavailable here.

## Private standards inputs

Aether-standards content remains private, including vendored releases, review
snapshots, copied checker scripts, hook tooling and copied examples/configuration.
Consumer-local architecture, decisions, adoption history remains
useful context. Private-focused adoption pages retain only availability notices.
References to absent standards are not public download promises.
Agent Temper is a separately sourced public method and retains its original pin.

The public source is therefore not a complete standards qualification workspace.
The broad `zig build test`, workflow/quality inventories and component aggregates
retain their private-input requirements. They may fail for missing inputs in a
public clone; do not skip those checks and call the full gate passed. Access to
private inputs and the relevant review remain prerequisites for work that needs
those contracts. Ask the owner through the owning issue before such work.
Ordinary public documentation, source integrity and the selected pure kernel
models can be checked within their stated scope. No missing standard is replaced
with a newly invented public standard.

## Public checks

The free Source checks workflow runs two bounded jobs on standard GitHub runners:

- Source integrity verifies the pinned Agent Temper bundle, selected Python syntax,
  workflow metadata JSON syntax, conventional PR titles and excluded private paths.
- Kernel models runs the four named pure Zig roots: capability, lifetime, native ELF
  and native launch. These currently contain 25 distinct test definitions; zero executed cases fails.
  The initial hosted run executed 29 cases because the four ELF tests also run
  through the launch root.

These jobs do not qualify a full kernel build, boot, persistence, shell, package
installation, recovery, private standards adoption or a release. Host/native
resource limits and outstanding gates stay with their contracts and issues.

See [GitHub maintenance](GITHUB.md), [development](DEVELOPMENT.md) and the
[onboarding issue](https://github.com/gonz0w/Aether/issues/1) for the current scope.
