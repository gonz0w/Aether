# Prepared bytecount: host package lifecycle

UL-056's actual userland bytecount 0.1 source now has an opt-in host recipe. This
moves the useful command's package lifecycle forward while native runner/bootstrap
acceptance is pending. It does not select bytecount for the base install or claim
an executable native Aether command. Userland retains command implementation and
base selection; pkg-mgr owns this source snapshot, recipe and package evidence.

The source and BSD license are copied from the verified 75-file UL-056 preparation
bundle, not fetched from a moving checkout during builds. [Origin pins](../recipes/bytecount/origin.json)
identify those exact bytes. The source metadata fixes SHA-256 and size. Future
source updates require deliberate snapshot/pin changes and new package checks.
The command itself is unchanged. Its package has no declared package dependencies;
the host compiler/libc/tool environment remains a trusted prerequisite.

```sh
sh tests/bytecount-integration.sh
```

This opt-in test requires a host C compiler and Python 3 for executable validation.
It does not download dependencies. It creates and retains a private root, rejects
same-size source corruption before extraction, runs the shell/make phases with
parallel make, builds/tests/stages/registers bytecount, exports its v2 directory
bundle, imports into a fresh initialized root, compares package records/licenses
and runs the imported executable. No live prefix, service or sibling is modified.

[Saved evidence](evidence/bytecount-package-2026-09-05/README.md) identifies the
retained root and exact manifests/records/artifact pins. Eleven host output/status
cases cover empty, six-byte, binary and multi-buffer input; invalid options and
locale; help and version. The same cases run during build, after staging and after
import. They are repeated lifecycle checks, not 33 independent features. Userland's
11 injected libc-call controls remain separate producer evidence, not rerun here.

The phase recipe stages the executable and original BSD license, then records the
host/compiler target and helper/recipe identities using existing package machinery.
GNU Make 3.81+ and POSIX sh remain the host baseline. Python is a development-test
dependency, not a bytecount runtime dependency or a new package-manager core.

To inspect the result, use the retained root printed by the test:

```sh
bin/pkg-mgr --root /absolute/retained/root --plain verify
LC_ALL=C /absolute/retained/root/stage/bytecount/usr/local/bin/bytecount --decimal < input
```

The binary is host-targeted. Native linking, two-record stdin/stdout bootstrap,
copied argv/env, command collection and exact service-side output verification
still require UL-057 and a completed matching command-runner producer. The runner's
EOF observation is not an independent byte comparison: the proposed broker owns
output readback. Preserve that evidence distinction in [native command acceptance](NATIVE-COMMAND-CONSUMPTION.md).
Hashes here establish identity, not source reproducibility, signer trust, sandbox
confinement, native compatibility or persistent installation.
