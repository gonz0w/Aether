# UL-076 — dash test-helper host compilation

Scope: test.py helper-build call only. It currently shares a direct-child subprocess
wrapper with remote Podman cases. Separate the trusted host compiler invocation into
an adapter over the unchanged command-runner process helper. Explicit cwd/private
environment, 45-second wait, 16 MiB file limit, owned session/descendants and retained
receipt are required before accepting a successful compile. Preserve helper-build
stdout/trace names, command fields and all twelve guest cases/markers.

Applicable: CP-01–03, E-01–08, local UL-063 process ownership; documentation changes
follow DP/DS, evidence follows EV. No tool/input/release pin or sibling edits. No new
supervisor/dependency. The wrapper/artifacts remain pinned by existing test preflight.
Trusted private paths and no concurrent mutation are assumptions. Owner SIGKILL and
detached hostile descendants are outside the helper contract. File limits also apply
to compiler output artifacts; the existing small helper fits 16 MiB.

Controls: stdout/stderr separation; explicit cwd/environment; timeout with descendant;
leader exit with surviving child; nonzero exit; missing executable; output exhaustion.
Run on qualified Python 3.10.21 and current 3.14.7. Compile actual helper.c using the
unchanged pinned retained cc.py/LLVM/SDK; compare its static ELF identity to previous
helper evidence. This is host compilation only; do not claim fresh guest execution.
Run quality gate and whitespace checks. Retain scripts, raw output, receipts and
source/tool/runtime hashes. Independent review remains pending.

Source review also covers build.py and generated cc-for-build.py: make/configure can
start remote target generators. Existing --rm and client timeouts do not establish
container reclamation after client interruption. Track UL-077 for unique per-attempt
container identity, creation/start ambiguity, bounded stop/remove and positive absence
checks against the same remote connection; test service failure and cleanup failure.
Do not install or restart Podman services as part of this host-only slice.
