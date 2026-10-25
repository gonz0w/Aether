# OpenZFS source feasibility evidence — 2026-09-06

[Assessment and next experiment](../../OPENZFS-FEASIBILITY.md).
This is source inspection only. No upstream build, engine execution, native boot,
resource measurement, signature verification or filesystem adoption occurred.

`identity.json`, `tag.json` and `tag-object.json` bind official OpenZFS 2.4.4 to
commit 71a9f9578616a90c3c14bb59629fb4d31bfd68d1. `source.tar.gz` is the unchanged
GitHub archive, retaining source notices and licenses. The full upstream source
is research evidence, not a dependency consumed by Aether builds.

Run the offline inspection from the repository root:

```sh
python3 docs/evidence/openzfs-review-2026-09-06/audit.py
```

It verifies the archive digest before reading eleven selected files and regenerates
`findings.json`. The 178 source entries and 30 pthread call names are lexical
source facts, not linked feature closure. Cache/stack/device constants are not
runtime measurements. Local implementation inputs are retained as
`aether-inputs.json` and `aether-inputs.tar.gz` (113 files); planning snapshots
are in `documents/`.

The first sandboxed curl request failed with exit 6 (DNS resolution). Retrying
with explicit network escalation fetched the tag identity, tag object and exact
commit archive successfully. There were no build attempts. The source archive was
hashed before extraction with Python's data filter; no upstream script executed.
Independent signature/authenticity checks remain pending.

The deliberate `tamper-control/` replaces the archive with explicit invalid bytes
while retaining the expected identity. Its saved command, input and log show exit 1
with `OpenZFS archive digest mismatch` before tar processing. This is an expected
integrity-control rejection, not upstream failure. Normal inspection passes.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returned zero; `host.log` retains kernel, offline standards/workflow and all 85
Python tests. No runtime/build source changed, so no QEMU regression was selected.
Local documentation links were checked. SHA256SUMS covers every retained file
except the manifest itself. Existing independent-review and extended-release
coverage remains pending; this evidence cannot establish release readiness.
