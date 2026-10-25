# Real dash main/init prerequisite review

Source review on 2026-09-08. The [contract review](../../NATIVE-SHELL-STARTUP.md#actual-maininit-prerequisites-review--2026-09-08)
records actual generated-init dependencies, hidden failure modes, ownership and
the next bounded diagnostic experiment. This turn did not execute dash init/main
or change runtime behavior. Prior 289-case signal-routine coverage stays scoped.

Fourteen exact reviewed inputs are preserved in inputs.tar.gz, named relative to
/Users/cam/DEV and hashed in inputs.json. Every member was read back and verified.
They include generated init/config, main/variable/directory/options code, actual
musl wrappers, current native dispatch and adapter, and reference build/license
receipts. Source inspection is not a new source-to-object rebuild claim. Original
notices are preserved; mutable sibling checkouts were only read for this review.

Validation: `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` passed, including 98 Python tests and host/pin/workflow checks;
see host.log. The simplicity manifest matched the recorded digest
8c3d8095acc9b6283a5f6970bc4ce6e7e4646a04fb759f8cf2940ed494cbeff8
and all four members were verified. Scoped diff whitespace checks passed.
No failed check or new target qualification. No sibling or released-pin change.

Next: diagnostic generated-init execution with a controlled environment and memory
grant; record missing PPID/user metadata and cwd semantics honestly. Positive real
main startup must follow truthful contracts, not fabricated successful calls.
Independent consumer review and full shell acceptance remain open.
