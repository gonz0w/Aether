# Native package prerequisite source review

2026-09-07 UTC. Documentation-only inventory of the existing init/import/list/
files/plain-verify/bytecount/reboot proposal. Reviewed branches and alternatives
are listed in NATIVE-PACKAGE-PREREQUISITES. This is not a complete syscall trace,
provider qualification, native execution, shared API or new runtime implementation.

Oracle: each documented helper/tool/identity boundary must be supported by the
selected source. Retain exact source and owner-tracking hashes. Unsupported native
admission and absent durability enforcement must remain visible; no renamed host
identity, publication grant, service activation or deletion authority is inferred.
Fresh development/standards/coverage checks validate document links and pins.
The first development check ran before this evidence README existed and rejected
that missing link; initial-check.json preserves the failed observation. No runtime
or native check was needed for this documentation-only change.

The source trace includes import's registration/manifest/hash/mode dependencies,
CLI plain rendering and default recipe parsing by init-root. SHA provider and stat
syntax branches are alternatives, not a demand to port every host tool. A target
build/provider selection requires its own complete dependency and error evidence.
inputs.json binds reviewed code, recipe/license and sibling tracking. No sibling,
immutable release, public protocol or candidate pin was changed.
