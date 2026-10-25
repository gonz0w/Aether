# Native init v1 producer evidence

2026-09-05. [Contract and invocation](../../NATIVE-INIT.md).

Seven new QEMU cases pass: conformance, wrong-deadline consumer, late-admission
consumer, supervisor exit, supervisor #UD, ignored kernel deadline, and skipped
cleanup zeroing. The shutdown cases require one live worker, one terminal worker,
two buffered bytes and one retained wait. Cleanup failures must panic without
`AETHER NATIVE INIT CLOSED`. The negative consumer results are exactly 701/702.

Regressions pass: 11 native-memory, 5 launch, 4 channel, 3 read-only files,
5 writable files, 12 frozen userland/sys-init legacy I/O cases, and the default
two-core smoke with framebuffer verification. Host kernel tests, 44 Python tests
and all three offline standards checks pass. The legacy consumer remains an
ABI-2/memory compatibility witness, not consumption of the new ABI 6.

`summary.json` pins the source archive, per-file source identities and suite
reports. Source hashes were checked against completed suite reports before
retention. `producer-sources.tar.gz` contains the kernel, fixtures, build scripts,
boot/toolchain pins, host tests and offline standards used for this checkpoint.
The suite folders retain small ELF/raw/envelope artifacts, maps, commands, source
and strict-libc/tool receipts, and serial logs. Large ISO/kernel outputs remain
at the explicit private paths in the reports. The strict musl SDK is a separately
required, hash-checked input; it is not bundled or automatically fetched.

`reviewed-sys-init-gates.md` captures the consumer questions examined for this
producer scope. No sibling source, immutable standard or consumer pin changed.
Sys-init's independently authored policy consumer and acceptance remain pending;
SI-01–03 must not be marked integrated from this Aether fixture. Real elapsed-time
service deadlines, blocking sleep, arbitrary helper delegation/revocation and
supervisor replacement are outside this bounded evidence.
