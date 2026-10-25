# Static record reference evidence

Decision 0112 documents all twelve static-tool settings fields, native-boundary
metadata/sites, source collection and lifetime, tool identity/order, report
fields and actual rejection behavior in docs/STATIC-RECORDS.md. Descriptive
metadata is distinguished from enforced checks. This is a local reference for
trusted maintainer inputs, not a shared standard or public ingestion API.

Five new focused tests pass: recursive versus immediate Python selection;
selected-source symlink and resolved-root escape denial; exact combined-byte
accounting with duplicate scope roots; comment/multiple-occurrence textual
boundary matching with line-drift rejection; and identical duplicate boundary
record rejection. They supplement the existing real rustfmt/Clippy, syntax,
tool-identity, deadline and output controls. The current real static success
report's exact field set was verified against the documented result shape.

All ten repository gates pass in out/checks/run-n1dguucj, retained in validation/.
The static reader, settings and boundary-inventory hashes match the previous
aggregate snapshot. All 24 native source inputs match the boundary-review
manifest. No executable, tool pin, release pin, native implementation, sibling
repository or historical evidence changed. No native execution or independent
technical/reader approval is claimed. No failed test/check attempts occurred.

The review identifies concrete follow-ups under BG-056: strict bounded JSON and
schema/type/duplicate-key validation before tool lookup, consistent structured
errors, ordinary-file/parent-symlink policy, settings/inventory identity during
standalone checks and complete host-tool dependency closure. Missing discovery
roots, permissive Python JSON and unchecked review metadata are documented
limits, not endorsed interchange semantics. Other record/API families and
installed reference/independent publication work remain open.
