# Package-state manual evidence — 2026-09-06

pkg-state(5) documents record layout, the ordered 19-key embedded evidence, names,
paths, modes, world/dependency inputs, verification, compatibility and preservation
limits. The checker compares key/order coverage to the current schema and checks the
required format-manual sections. It rejects new pages outside the checked inventory.

Both manuals pass strict mandoc lint, HTML and 60/80-column terminal rendering.
Narrow rendered text and examples were inspected; the checker also rejects overflow.
Curated examples register hello-local, mark it explicit, observe a non-deleting
empty orphan report, and require duplicate world roots to fail without partial output.
The private world fixture is restored after that negative case.

The host man command finds and displays pkg-mgr(1) and pkg-state(5) under private
share/man/man1 and man5 directories. Lookup output must name the staged path, not
another installed page. Input and tool identities and the retained fixture root are
in the JSON records. This does not constitute a produced release artifact or native
Aether documentation lookup. No runtime package or file-format behavior changed.

Three negative controls reject evidence-key drift, an unchecked new manual page,
and missing required man lookup tooling. Required rendering/lookup fails closed;
ordinary developer checks can report an optional missing tool as NOT RUN.
This documentation-only change used curated workflow, renderer, development and
standards checks; the unrelated full runtime suite was not rerun. Binary-format
manuals, actual candidate packaging and independent reader/release review remain open.
