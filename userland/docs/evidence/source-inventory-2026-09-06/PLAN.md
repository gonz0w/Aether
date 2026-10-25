# UL-074: maintained-source inventory and review adoption

Record the user's explicit approval of the manual-review packet without inventing
commands, platform logs or detailed findings. Bind reviewed implementation/manual
bytes to the previous handoff. Preserve historical pending records. Scope technical
acceptance to UL-072; package/target lookup and broader migration remain separate.

Local work: snapshot maintained source paths and exact bytes, language scope,
subsystem documentation and existing evidence routes for UL-061/063. Inventory
root contributor tooling and experiments, including extensionless Git hooks;
separately classify vendored, generated and historical material. Do not execute
unknown scripts to discover help; static parser/entry-point hints are not supported
CLI assertions. Python AST parsing is discovery only, not minimum-version runtime
proof. Imported/generated source embedded in builders needs a separate review.

Apply DP-01/02, DS-03/05, TC-01, CA-02/03, CP-01–03 and EV-01–05 from the
unchanged approved snapshot. No release pins, native runtime source or sibling
changes. Existing upstream style/notices and immutable evidence remain intact.
No new dependency or product API; use standard-library discovery in a retained
build script. Check discovered paths against Git tracked inventory, local file
existence, source digests, stable coverage routes and explicit unclassified entries.
Meaningful controls reject omitted/duplicate/changed/foreign-source records.
The source snapshot is not a new automatic build dependency or formatter rollout.

Run local quality, source inventory validation and whitespace checks. Record exact
commands/results, Python and source identity. Missing independent source audit,
manuals, minimum-version runs and native evidence remain missing; this task must
not promote a file to verified based solely on a matching hash or parser hint.
