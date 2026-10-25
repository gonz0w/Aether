# Boot the developer lab kit

This is an x86-64 UEFI VM kit for the qualified three-parent serial-session
workload. It boots Aether and actual interactive dash, retains shell state across
three prompts, runs the bounded helper and pipelines, and checks shutdown/cleanup.
It uses the existing owner-issued grants and finite fixture limits. SSDK-06 review
is deferred. Physical hardware, unrestricted sessions, persistent storage, login,
general TTY/job control and packaged sys-init integration remain later work.

Use QEMU11.1.1 with the kit's firmware for the qualified VM configuration. In a
fresh copy of the kit directory, make a fresh writable variables image:

```sh
cp -n vars.fd session-vars.fd
qemu-system-x86_64 -machine pc-q35-11.1 -accel tcg -cpu qemu64 \
  -smp 1 -m 256M \
  -drive if=pflash,format=raw,readonly=on,file=code.fd \
  -drive if=pflash,format=raw,file=session-vars.fd \
  -cdrom aether.iso -boot d -nic none -vga std -display none \
  -serial stdio -monitor none -no-reboot -no-shutdown
```

Wait for the real `$ ` prompt before supplying each command. The command files
are three single-line inputs; print them in another terminal and paste each line
once at its matching prompt. Repeat for each of the three fresh parents. Each
parent checks argv/environment, both pipelines, substitution, retained variables,
parent identity and descriptor closure, then exits. Inputs must follow prompts;
preloading all phases does not demonstrate an interactive session. Kernel smoke
and terminal/reclaim records appear alongside shell output and remain unchanged.
The retained VM smoke test automates this exact exchange and checks bytes/lifetimes.

Keep the receipt beside the kit: it binds the SDK rebuild, payload, kernel/modules,
ISO, firmware and tools. A successful build is separate from a successful boot.
Stop the QEMU process after the fixture completes; no guest shutdown/restart or
physical-media installation command is supplied by this experimental kit.

The ISO is copied byte-for-byte from the qualified artifact after inspection.
Original Aether material is BSD-2-Clause. It contains musl, dash and Limine with
their existing upstream terms; licenses/ and the SDK candidate retain notices.
This developer artifact is not a supported distribution or a published SDK.
