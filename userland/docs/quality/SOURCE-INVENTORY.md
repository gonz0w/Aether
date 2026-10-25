# Maintained-source census — UL-074

The [snapshot](source-inventory.json) records exact bytes for 180 tracked source
and patch files at the recorded base commit. It routes each file to subsystem
coverage and documentation. This is discovery, not source-audit acceptance.

There are 81 Python files, 73 C files, 22 C headers, two shell hooks and two
patches. Python AST inspection found 72 direct `subprocess.*` call sites; these
are review leads, not 72 defects. Aliases, indirect calls and embedded generated
code are not covered by that search. No scripts were imported to infer supported
CLI behavior. No Rust, Zig, assembly or Makefile appears in this maintained-path
selection; generated programs and upstream build trees still require scoped review.

Pinned vendor inputs, historical evidence and private build outputs are excluded
from maintained-source migration. Exclusion does not remove the obligation to
audit consumed generated/imported code. The copied Git hooks are routed separately;
preserve their shared owner and notices. Non-source assets and configuration need
separate public-surface inventory under UL-061.

## Next local work

- UL-061: expand subsystem routes into supported commands/options, configuration,
  tests and manuals, beginning with the host experiment entry points. A route to a
  README does not establish that every option or failure is documented.
- UL-063: inspect the remaining Python process boundaries against explicit cwd,
  environment, timeout, exit and descendant-cleanup requirements. Use the static
  call sites to select scopes; retain existing command-runner and quality evidence.
- UL-063: finish C and embedded/generated Rust/FFI review, language-tool identities,
  selected CERT mapping and scoped suppressions. No formatting sweep is authorized
  by this inventory.
- UL-062: bind workload/instrumentation coverage to these scopes before claiming
  extended test completeness.

The dated [evidence packet](../evidence/source-inventory-2026-09-06/README.md)
retains discovery and omission/duplicate/drift controls. Regenerate as an explicit
reviewed snapshot after source changes; this inventory is not an automatic build
pin. Its coverage entries remain draft pending actual audits. Existing release
pins and native producer dependencies are unchanged.
