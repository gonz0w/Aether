# First-release scope change — 2026-09-06

Maintainer replaces the M4 demo release boundary with R1: boot through sys-init
into a serial shell, working runner, persistent filesystem and native package
management. Serial console is explicitly accepted; native NVIDIA is deferred.
Planning and contributor entry points were aligned; no runtime change or sibling
acceptance is claimed. Persistence across reboot is the stated interpretation of
the system goal; engine and initial snapshot/rollback extent remain decisions.

Exact document snapshots/hashes and the local host/standards/workflow command
interval/result are retained. No native runtime change required a QEMU rerun.
Existing third-party, independent-build and release-review gates still apply
to the eventual complete R1 image; this is scope authorization, not publication.
