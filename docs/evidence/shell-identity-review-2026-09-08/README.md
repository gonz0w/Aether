# Bounded startup identity contract review

Documentation-only review on 2026-09-08. The [contract](../../NATIVE-SHELL-STARTUP.md#bounded-startup-identity-contract-review--2026-09-08)
defines an opt-in direct-launcher parent query and its acceptance tests. It separates
parent identity from launcher/session-supplied compatibility user/group metadata.
No new runtime behavior, authentication, consumer adoption or pin change.

Nine exact local inputs are preserved in inputs.tar.gz and inputs.json; every
member was read back and hash-verified. The earlier generated-init packet remains
the runtime evidence for missing metadata. This review does not requalify it.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
passed, including 98 Python tests and host/pin/workflow checks; see host.log.
The simplicity snapshot manifest matched the digest in STANDARDS and all four
members verified. Scoped diff whitespace checks passed. No fresh QEMU selection
for this documentation-only change. One initial read used a nonexistent
Foundations filename; the actual OWNERSHIP.md was then read successfully.
No sibling files were modified. No independent owner/reader acceptance is claimed.
