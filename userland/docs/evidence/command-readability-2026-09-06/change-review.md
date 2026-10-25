# UL-063 CSR-03 Python readability

Before-edit plan: use explicit main entry points in three drivers, expand dense
statements, remove unused imports, name source paths in the client builder.
Apply CP-01/02/03, TD-01/03, TE-01/03 and Foundations E. Preserve command order,
flags, argv, environment, pin checks, process cleanup, all case expectations and
receipt schemas. No new dependency, C or shared-interface change.

Risk is altered execution order or closure scope during restructuring. Review
normalized AST before/after and compare runtime command/case inventories with
prior C17 receipts, normalizing only private output roots. Run 21 host/control
cases, five ELF identity comparisons, all nine native cases, seven process
controls, import-without-work controls and Python 3.10 grammar checks. Actual
host interpreter identity retained; other supported interpreters are not run.
Use existing explicit tool/SDK pins, private build roots and process bounds:
30-second host, 180-second build/smoke process, 30-second guest watchdog. Native
suite budget 15 minutes. Keep every failed attempt and final logs/receipts.

Record review, sources, docs/inventory and quality check. Current task supplies
technical review; independent technical/reader reviews remain pending. No public
runner implementation, affected-owner acceptance or UL-063 completion claimed.

Actual review: current Codex task verified normalized execution AST equality
except the declared main/named-source/expectation-helper substitutions. Both pure
expectation helpers match original expressions for all nine cases (18 checks).
All selected runtime tests pass, as do command argv/exit and five ELF comparisons.
No additional sanitizer run for Python-only restructuring; unchanged C behavior
has direct native regression evidence. UL-062 broader instrumentation remains.
Imports are inert in three observed imports; process controls independently cover
timeout/descendant handling. Independent technical and reader reviews pending.
