# Launcher-supplied user/group metadata review

Documentation-only contract review on 2026-09-08. The
[local experimental specification](../../NATIVE-SHELL-STARTUP.md#launcher-supplied-usergroup-metadata-review--2026-09-08)
defines AECAT002, staged admission, informational C getters, version handling,
authority limits and the required native controls. No runtime implementation,
raw credential API, authentication or affected-consumer acceptance is claimed.

Twelve exact inputs are preserved in inputs.tar.gz and inputs.json; all archived
members were read back and SHA-256 verified. Host checks passed via
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`,
including 98 Python tests and pin/workflow checks; see host.log. The simplicity
manifest matched the STANDARDS digest and its four files verified. No failed check
or fresh QEMU selection for this documentation-only review. Release pins and
sibling repositories remain unchanged.

Next: implement the selected sender/decoder/getters and invalid-record cleanup,
then qualify actual dash init with explicit launcher-supplied metadata. Raw kernel
UID/GID calls remain unsupported. Directory support is still a separate gate.
