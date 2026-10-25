# UL-073: minimum-series Python execution and reviewer handoff

User authorized provisioning and practical unblock steps; user will perform the
independent review manually. Build official CPython 3.10.21 and 3.12.14 sources
under build/python-qualification, never a real prefix. Verify SHA-256 against the
HTTPS Python.org release pages before extraction/execution. Retain upstream license,
source pin, compiler/build commands, logs and runtime identities. This is host
qualification of the quality checker, not a supported target Python distribution.
No release standards pins or sibling sources change. No signing verification claim.

Apply CP-01–03, CD-01/04, TD/TE, DW/DM/DP and EV-01–05. Use existing Clang 21.1.8,
GNU make 3.81 and host SDK; no pip, package install or dependency upgrade. Tool
inputs are host facilities, not an independently reproducible bootstrap closure.
No application SSL/network or complete CPython build qualification is claimed.

Each source build uses 4 make jobs, 600-second deadline, recorded process ownership
and bounded logs; source archives/build outputs stay under build. Run the existing
8-method/10-case process suite, quality gate, release rejection, and CLI regressions
with each exact interpreter. Treat unsupported modules, compilation or test failures
as failures of their affected scope. Preserve all attempts and large local artifacts
by path/hash. Tests require actual execution, not only grammar checks. Later patches
within a minor series do not prove compatibility with every earlier patch release.

Prepare a manual review packet binding commits, exact paths, instructions and return
fields. Leave reviewer decision empty until the user supplies findings. No messages,
new tasks or fabricated sign-off. Prior browser file-URL rejection remains recorded;
do not work around it. User can inspect the local manual independently.
