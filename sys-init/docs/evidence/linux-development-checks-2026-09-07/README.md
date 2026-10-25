# Current Linux development-check attempt — 2026-09-07

Decision 0150 records partial qualification, not a passing Linux aggregate.
The cached image ID/digest matches the previous EHT-01 witness. Containers used
read-only source, no pulls/network, private tmpfs, resource limits and named cleanup.
Commands, raw logs, all attempts and driver scripts are retained here.

The first full run omitted .planning in its snapshot and failed quality. Adding
those required records let the second run pass standards, experience, distribution
and quality, then block at the absent reviewed Linux-aarch64 rustfmt identity.
Separate diagnostics passed native-evidence, model and host. The harness ran 213
tests with two fixture-assumption failures and one missing-rustup error. Sample
receipt setup first failed on read-only /work/out. No failure was counted as a pass.

The fixture already mocked tools but used the actual host platform. It now selects
the pinned fixture platform explicitly. Five focused Linux tests pass. Supplying a
private writable /work/out makes sample setup reach the missing rustup lookup;
zero sample tests execute, so that gate still fails. The rustup diagnostic's exit
zero means the lookup ran; its printed None means the tool is absent.

All ten macOS gates pass in validation/. Linux native-audit stdout exactly matches
macOS. Native inputs, catalog and three release locks remain unchanged. The full
Linux source maps predate the one test correction and final process/inventory edits;
review.json lists those differences. Earlier failed bytes are retained in
static-inputs-before.py. Only the focused test was rerun after that correction.

The large private source snapshot remains in the recorded out/linux-full directory;
it is not duplicated in this bundle. Aggregate source maps, existing immutable
repository evidence, changed source copies and command logs establish the scoped
record; this is not an independently complete source archive. Prior failed reports
are immutable, even where running sample receipts stopped during tool lookup.

Next provision the required Linux Rust 1.98.0 compiler, rustfmt and Clippy, review
platform-specific identities, and rerun the full gates with private writable out.
Existing tool pins were not changed, no software was downloaded and no sibling
repository was modified. EHT-01's 432 Linux passes remain their separate witness.
No independent sign-off, BSD/illumos, hosted scheduling or release acceptance follows.
