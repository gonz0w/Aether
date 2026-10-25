# Binary manual validation — 2026-09-06

Scope: HR-05 host documentation for the experimental preview. No runtime source
changed. The oracle is the documented ordered fields and actual bytecount bundle;
missing fields, different inventory/digest bindings, unchecked pages, failed examples
and unusable required rendering/lookup must reject.

`python3 tests/check-manuals.py --render-required --binary-example` passes on the
host recorded in result.json. All three pages pass strict mandoc lint, HTML and
60/80-column text rendering and private staged `man -M` lookup/display. The rendered
binary manual was inspected at 60 columns. The bytecount workflow verifies source
tamper rejection, build, registration, export, fresh-root import and execution. The
checker separately verifies exact bundle inventory, ordered descriptor/target keys
and four table digest bindings. A deliberately changed descriptor key fails before
running examples; negative-control.json retains the observation and private root.

accepted.log and binary-example.log retain successful output. result.json records
manual/tool identities and platform; input-sha256.json records the exact dirty-tree
source inputs, including the checker, recipe and lifecycle fixture. Generated roots
remain private and retained; these hashes do not identify a clean release candidate.

Two earlier checker attempts failed: initial-key-check.log records a field regex
that excluded digits in SHA-256 key names; initial-lookup-check.log records a display
check that did not strip terminal overstrikes. Both checker assumptions were corrected
before the accepted run. Neither failure demonstrated a package-manager runtime bug.

The selected follow-up gates are whole-shell development lint, pinned standards and
whitespace checks, recorded in separate logs. The unrelated sixteen-fixture runtime
suite was not repeated for this documentation/checker change. Compiler-free normal
manual checks still report the optional binary example as NOT RUN.

Actual release packaging, independent reader/technical review, broader release
qualification and publication approval remain pending. Host lookup is not native
Aether lookup; digest identity is not remote authentication or durability.
