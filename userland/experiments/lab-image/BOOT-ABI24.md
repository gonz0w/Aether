# Boot the ABI24 developer lab kit

This x86-64 UEFI VM kit boots Aether and one actual interactive dash session.
The qualified workload retains shell variables and parent identity through three
commands, runs the fixed helper, pipelines and substitution, and checks ten
terminal/reclaim lifetimes before the owner closes UART and halts. Channel waiting
has been exercised with 35 seconds of idle at a real prompt. The finite image,
capability and child-generation limits remain in force. This is a developer
fixture; physical hardware, login, storage, general TTY/jobs/signals and packaged
sys-init composition remain separate work. SSDK-06 reader review stays deferred.

With QEMU11.1.1, use a fresh writable copy of the supplied variables template:

```sh
cp -n vars.fd session-vars.fd
qemu-system-x86_64 -machine pc-q35-11.1 -accel tcg -cpu qemu64 \
  -smp 1 -m 256M \
  -drive if=pflash,format=raw,readonly=on,file=code.fd \
  -drive if=pflash,format=raw,file=session-vars.fd \
  -cdrom aether.iso -boot d -nic none -vga std -display none \
  -serial stdio -monitor none -no-reboot -no-shutdown
```

Wait for `$ ` before each input. In another terminal, print command-1.sh, then
paste its single line at the first prompt. Repeat with command-2.sh and
command-3.sh at the next two prompts. The third command exits the shell and the
owner halts after cleanup. Stop QEMU after the final `NATIVE init halted` record.
Do not preload commands: the qualification checks prompt-driven input, exact
bytes and child cleanup before each next prompt. Original kernel records remain
mixed with shell output on serial, with their exact test markers preserved.

The receipt beside this kit binds the SDK rebuild, exact ISO components, firmware
and tools. Build success and native boot evidence are separate. The ISO is copied
from the qualified composition after readback. Aether code is BSD-2-Clause; musl,
dash, Limine and firmware retain their own terms and supplied notices. This kit
is neither a published SDK nor a supported distribution. It supplies no physical
media installation procedure or automatic host service changes.
