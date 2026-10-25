# Supervised transport in the development gate

`sh tests/check.sh` now includes `tests/aether-supervised.sh`, a POSIX shell
entry point that execs the existing Python transport test. It runs immediately
after boot v2 within the runner's disposable checkout. A missing interpreter or
failed transport check fails the normal gate; no skip path was added.

The existing test covers one valid synthetic six-artifact transport and seven
rejections: wrong native pin, malformed envelope, existing publication, wrong
receipt pin, modified payload, extra file and symlink. It does not boot its
synthetic ELF. Saved QEMU/native evidence remains separate.

[Full run](fixtures.txt): `sh tests/check.sh`. Python was already required by the
standards and CLI development tests. The optional host transport, package runtime,
shared standards/pins, native ABIs and fixture assertions were not changed.
