# Actual-main native ENV guard build selection

The three-object comparison and host/pin/workflow checks (98 Python tests) pass. Original and patched-disabled main objects
have no UID/GID getter imports. Enabling AETHER_NATIVE_ENV_GUARD adds exactly
getuid/geteuid/getgid/getegid, with no other import difference. Preprocessed source,
relocation disassembly, exact commands, stdout/stderr and object digests are retained
under the directory named by build.log. Native execution is NOT RUN. Existing32
reference objects and all runtime profiles remain unchanged.

inputs/env-guard.patch changes only the preprocessor condition around the existing
upstream identity-equality guard. It does not globally undefine Linux macros,
regenerate configuration, rewrite ENV loading or implement privileged execution.
The copied main and headers retain upstream notices and COPYING.dash; SDK headers
retain musl terms (COPYRIGHT.musl). Original experiment tooling is BSD-2-Clause.
The candidate is not installed and is not a completed full-dash delivery.

inputs/reference-sources.json matches the digest in the existing reference summary.
Copied upstream source/header bytes match that source manifest; config.h matches
the existing build receipt. Generated headers are captured from that build tree
with fresh hashes, not independently regenerated here. All copied SDK headers are
pinned in inputs.json; this is a retained local SDK snapshot, not fresh SDK/source
authentication. Existing source authenticity and generator review limits remain.
The build verifies all input hashes and tool executable hashes before and after.
No sibling files or release pins were modified. No failed compile attempt occurred.

The current consumer checkpoint has reproduced323 command cases. Producer delivery
is now the [360-case queued-body packet](../shell-queued-body-2026-09-09/README.md),
which also retains its failed initial attempt and verifies the predecessor chain.
The intervening poison/PWD/boundary/allocation/metadata packets remain available;
consumer reproduction/acceptance is pending, not inferred from producer checks.

Run from the repository root:

```sh
python3 docs/evidence/shell-main-config-2026-09-09/build.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Each comparison creates a separate retained output directory. This one-off receipt
is not a new runtime launch profile. The [configuration contract](../../NATIVE-SHELL-STARTUP.md#actual-main-env-configuration-selection--2026-09-09)
defines actual-main ENV execution acceptance: equal identities versus separate
UID/GID mismatches, interactive/noninteractive, absent/empty ENV, omitted-guard
mutation, closure and reclaim. This pinned options table does not implement -p;
its illegal-option behavior must be tested, not treated as a privileged mode.
Login profiles and authenticated/secure launch policy remain separate. Next wire
the candidate into a separately selected actual-main fixture, run these controls,
then the existing userland argv/signal/syntax and exec/wait workloads.
