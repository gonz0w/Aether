# 0016: Consume an available cached Linux environment

Accepted 2026-09-05 for BG-054/BG-040. Podman reports an existing running applehv
VM and a cached Aether-userland reference image. Run the ordinary offline checks
against a frozen sys-init snapshot with an exact local image ID, no pull/network,
read-only root and source mount, private writable report mount/tmpfs, dropped
capabilities, no privilege escalation and bounded process/memory/CPU resources.
Do not build/download an image, start another VM, change companion sources or
configure a CI provider for this experiment.

Record the image identity, container command, Python/kernel/platform, source
hashes and every actual result. A missing tool or platform failure cannot be
reported as a passing or skipped suite. Test-owned children remain bounded; orphan
helper reaping limitations are not erased by container execution. A passing Linux
container is Linux host-adapter evidence under this environment, not bare metal,
BSD/illumos, native Aether or supervisor-crash containment. A frozen writable report
mount is not permission to alter source inputs. Retain failures before fixing
local portability issues and rerunning. Existing native workloads remain separate.
