# Supervised native boot transport

Optional Python 3 host experiment; the shell package manager and legacy transports
retain their dependencies and exit contracts. This extends a verified five-file
v2 handoff with the explicitly pinned AENSUP01 service/supervisor envelope.
Installation and staging never run the service. Python is already a host image
builder dependency; this is not a required target runtime or core package helper.

From an initialized private root containing a current matching aether-boot-v2 bundle:

```sh
python3 mk/aether-supervised.py stage ROOT BASE_RECEIPT_SHA256 SUPERVISED_BIN NATIVE_SHA256
python3 mk/aether-supervised.py verify ROOT/aether-supervised-v1 RECEIPT_SHA256
python3 tests/aether-supervised.py
```

Stage prints the new receipt pin last. Keep it outside the bundle. The new bundle
contains exactly receipt.json plus aether, protection.bin, display.bin,
lifecycle.bin, smp-supervisor.bin and native-c.bin. It binds the v2 receipt and all
six payload hashes. Source-to-binary correspondence is established separately by
build evidence; hashes do not prove authenticity. The supervised envelope header,
lengths and ELF identity are checked here; semantic compatibility needs boot tests.

Use Aether's matching image builder with these six named payloads, in that order
(kernel first, native-c.bin last), followed by its `scripts/supervised_smoke.py`.
The kernel must have been built with `-Dsmp=false -Dnative-c-image=SUPERVISED_BIN`.
The staged image passed `AETHER NATIVE SUPERVISION PASS`; the receipt, source
inventory and serial evidence are retained in docs/evidence/native-supervision-2026-09-05/.

The transport test accepts one valid synthetic transport and rejects wrong input
pin, malformed envelope, existing publication, wrong receipt pin, changed payload,
extra file and symlink. It does not claim its synthetic ELF can boot. The normal `sh tests/check.sh` gate now runs this test through
`tests/aether-supervised.sh`, alongside the other fifteen fixture scripts.
Python 3 is already required for development checks; the transport remains an
optional host tool, with no new target runtime dependency.
Private single-writer roots are required. No hostile filesystem-race protection,
power-loss durability, cryptographic trust, enablement or activation is claimed.
Operational rejection exits 1; argparse usage exits 2; success exits 0.

An explicit [native-memory transport](NATIVE-MEMORY-TRANSPORT.md) now handles the
AENFD001 descriptor consumer with required memory-enabled/single-core build options.
It uses a separate destination and receipt format; this legacy profile is unchanged.

[Dual-image launch, channel and read-only file-service transport](NATIVE-LAUNCH-TRANSPORT.md)
now uses explicit profile commands and separate receipts. All remain inert during
staging; the consuming boot witnesses are opt-in and independently pinned.
