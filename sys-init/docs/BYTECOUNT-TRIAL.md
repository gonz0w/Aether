# Native bytecount file trial

Issue18's dedicated prerequisite uses the Rust Owner to stage the pinned
bytecount in /pkg and execute it as one direct child. Seed creates one directory
and three files, writes eleven executable chunks and abcdef, and permits one
child write of 6 plus LF. Cold reopens and verifies the same files, then permits
one output overwrite. The Owner verifies input and output after child reclaim.

The private kernel selector is `-Dnative-package-bytecount=true`, with AENFS008,
124 KiB of Owner RX, and a guarded 48 KiB Owner snapshot at 0x904000 inside the
existing backing. The file snapshot is fully checked against the pinned ELF.
A native launcher supplies the exact argv and environment and waits for child
exit0. Authenticated startup binds stdin to FILE3 and stdout to FILE4.

Build the guarded SDK and runtime as described in R1-ZSH-SOURCE.md. Use the
same pinned tools with `r1-zsh-source.py --bytecount-only` to produce the child
and launcher. The Owner builder has package-seed and package-cold roles,
consuming that child through --probe. The engine builder has the same roles
and consumes it through --package-elf. The image builder checks their exact
role lock through --source-inputs.

After review and image admission, run from the repository root:

```sh
python3 -B sys-init/scripts/run-bytecount.py seed "$work/session" \
  --image "$work/image-package-seed" --image-report-sha256 "$seed_report_pin" \
  --qemu "$qemu" --firmware "$PWD/.deps/firmware" \
  --fixture "$sources/testpool_zstd.tar.gz"
python3 -B sys-init/scripts/run-bytecount.py cold "$work/session" \
  --image "$work/image-package-cold" --image-report-sha256 "$cold_report_pin" \
  --qemu "$qemu" --firmware "$PWD/.deps/firmware"
```

Each stage is single use. Cold checks the successful seed receipt, stopped disk
identity and digest. Both use the existing no-network watchdog and known-stop
capture. Require exact Owner file/output receipts, all three normal exits and
reclaims, terminal restoration, filesystem export and halt. Preserve failed
attempts and stop the cohort at its first unexpected result.

Focused checks include check-package-stdio.py, package policy/receipt controls
in the filesystem service README, and affected kernel and image/serial controls.
Full package import and its shell/tool process tree remain under issues17/18.
