# Preview input and setup review — 2026-09-06

Scope: owning-task component/notice review and installed-host setup observations,
not a public source allowlist, independent approval or licensing clearance.
The intended preflight result is a retained tool identity/probe report; missing
required tools, failed probes, unsupported host profile and wrong required lint
version must block. No tool installation or package-manager runtime change.

`python3 tests/check-host-setup.py` passes on macOS 27.0 build 26A5421a, arm64.
host-setup.json retains command outputs, including Apple probe stderr, tool paths
and hashes. Apple cc/make command shims have identical bytes; xcrun-selected clang
and make have separate identities. SDK 27.0's settings identity is recorded.
This supplements the earlier snapshot witness; it does not retroactively prove the
complete toolchain identity of that earlier run. SDK content closure, installation
inputs, override-specific build coverage and an independent witness remain open.

negative-controls.json records two fresh runs using temporary tool directories:
no required tools and ShellCheck 0.10.0 each return nonzero with a blocked receipt
and the exact expected reason. Required tool availability is not semantic build
coverage; existing full-suite/compiler checks must still run for candidate bytes.

notice-checks.json verifies bytecount.c and LICENSE against origin.json, source.kv
hash/size agreement and root/license equality. The three pinned standards locks
are identified separately and their normal offline gates pass. Existing license,
fixture, origin and vendored release bytes were not modified. The content review
preserves the advisory fixture's declared CC0 data license and distinguishes
original recipes from unbundled upstream payloads and installed host tools.

active-inputs.json records exact paths/hashes inventoried in the active source scope,
excluding archived/evidence trees. policy-input.json records the read-only canonical
licensing-policy identity. Neither is a selected public release inventory. Review
scope and remaining decisions live in RELEASE-CONTENTS and HOST-RELEASE.

Selected validation: installed-host preflight, missing/wrong-tool controls, bytecount
origin/notice comparisons, whole-shell development checks, pinned standards and
whitespace checks. No unrelated sixteen-fixture runtime rerun for this opt-in
setup-check and documentation change. The previous relocated suite remains scoped
to its own archive hash. The user was asked for a monitored security contact and
triage owner; no placeholder or invented answer closes that publication gate.
