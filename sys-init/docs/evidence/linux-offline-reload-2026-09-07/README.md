# Offline Linux image reuse — 2026-09-07

Decision 0152 checks the saved OCI archive SHA-256, loads it in a new Podman
session, verifies exact image ID/Linux arm64, then runs EHT-01 with no pulls or
network. All eight seeds pass all 54 cases (432 executions, zero skips). Complete
worker records match the original campaign. Rustc, cargo, rustfmt and Clippy
identities/versions match before and after. Named container cleanup succeeds.

reload/ retains exact commands, raw load/inspection/campaign logs, worker results
and tool identity records. reload-driver.py is the executed orchestration and
references the existing 0151 read-only snapshot and private tool homes. Large
working artifacts remain under out as documented in LINUX-DEVELOPMENT.md. The
new campaign matches current implementation/corpus hashes; it is not another full
Linux ten-gate run. That full-suite witness remains decision 0151.

validation/ and checks.log retain ten passing current macOS gates with unchanged
sources during validation. Native audit stdout, 24 native inputs, catalog and
release locks remain unchanged. No sibling, runtime or tool pin changed.

QEMU executables are available; no BSD/illumos image was found under repository
out and no git remote is configured. These scoped observations are not an
inventory of every machine or image on the host. Next work is additional guest
provisioning, actual independent technical/reader review and a selected hosted-CI
provider/remote. Repeated Linux checks cannot establish those requirements.
