# Build and public-command coverage review

2026-09-07 UTC. Documentation-only review adds ten groups (65 total). No runtime,
test, pin or sibling changes. Aether remains the sole release target.

Oracle: new anchors resolve uniquely and describe actual assertions. Reuse of the
recent full suite requires exact equality of all bin/mk/tests/recipes/fixtures/
manifests entries and a passing watchdog receipt plus both fixture completion
markers. New static checks validate inventory, coverage controls and pinned standards.
No new runtime execution is claimed for this documentation-only update.

## Remaining gaps identified by the review

- CLI machine-view comparison covers list/owners/verify/orphans on an empty private
  root. It does not cover every populated-state view or mutating-command adapter.
- Help-name/manual agreement is vocabulary coverage; it does not prove dispatch,
  argument forwarding, emitted receipts or exit semantics for all 13 commands.
  Review existing binary/receipt fixtures before adding missing command cases.
- Escaping checks use selected byte sequences and substring assertions, not a full
  terminal protocol, accessibility or adversarial presentation certification.
- Several build rejection cases accept generic nonzero. Existing named corruption
  and publication markers are stronger; complete cause-specific rejection remains
  a scoped follow-up rather than an inferred guarantee from the group count.
- Serial versus -j8 ordering in one controlled invocation is not concurrent-writer
  safety. Compiler-backed zlib/zpipe/bytecount work remains opt-in; synthetic build
  fixtures and private staging do not qualify native package installation.

source-match.json binds the original dirty manifest, full log and watchdog result.
Historical failed evidence remains unchanged. The next bounded work is a command
acceptance gap review leading to missing semantic tests, not more release claims.
