# 0122 — Private verified standards execution

BG-056 host slice, 2026-09-07. Run the reference child from a private temporary
release tree containing only captured, hash-verified manifest payloads. Recheck
the staged tree before/after successful execution and retain original pre/post
checks. Clean the temporary tree on normal/error unwinding. Limit staged payloads
to 64 MiB total as well as existing per-file/traversal limits.

Use the current interpreter with -I -S -B: ignore Python environment path/options,
exclude user site and automatic site initialization, and suppress bytecode writes.
Assertions stay enabled for all three families. Preserve non-Python environment,
working directory, inherited output and wrapper exit contracts. Trusted interpreter
and standard library remain host dependencies; this is not an OS sandbox or proof
against same-user mutation. SIGKILL cleanup and child deadlines remain open.

Pinned checkers use __file__-relative data and explicit Distribution policy-file
imports, so staged paths retain their layout. Test real staged execution, original
mutation at dispatch, import/optimization controls and cleanup on errors. Run all
focused and aggregate gates; preserve pins, native inputs and release bytes.
E-01–08 apply in this bounded host scope. No shared ABI or sibling edits.

Validation: eighteen focused tests pass (14 standard-wrapper/input/identity/private
tests and four offline-lock tests). All ten gates pass in out/checks/run-celvo_l3.
All three real released reference outputs match decision 0121; pins and 24 native
inputs remain unchanged. Twelve manual commands pass. Captured evidence:
../evidence/private-standards-execution-2026-09-07/README.md.
