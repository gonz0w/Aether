# Persistent serial Zsh developer boot

This recipe uses the sys-init filesystem-session Owner, the existing
OpenZFS engine and the #170 note workload. The Owner waits for the exact
engine to attach ROOT and HOME and publish readiness before admitting
Zsh. The shell prompt also requires the subsequent startup exchanges.
The serial and process adapters run in the existing Owner.

Run the commands from the repository root. Provide Python 3, the tools in
`boot/dependencies.json`, a Rust compiler with the bare-metal target,
the checked Limine and firmware inputs under `.deps/`, and the supplied
offline inputs listed below. Use absolute paths to the tools, the input
files and a private directory for disposable outputs.

| Role | Supplied inputs |
| --- | --- |
| Seed image | `zsh-login-startup-writer-2026-11-07-v1` and `fs-launch-terminfo-nine-2026-11-07-v1` |
| Note image | `zsh-operator-note-2026-11-09-v1` and `fs-launch-operator-note-2026-11-09-v1` |
| Seed disk | The pinned upstream `testpool_zstd.tar.gz` identified by `scripts/openzfs_namespace.py` |

The builder checks the seals and complete envelope. To produce inputs from
a clean checkout, use the [R1 source build](R1-ZSH-SOURCE.md).

```sh
python3 -B sys-init/scripts/build-persistent-zsh.py seed "$work/seed-image" \
  --app-seal "$seed_app" --engine-seal "$seed_engine" \
  --zig "$zig" --rustc "$rustc" --xorriso "$xorriso"
python3 -B sys-init/scripts/build-persistent-zsh.py note "$work/note-image" \
  --app-seal "$note_app" --engine-seal "$note_engine" \
  --zig "$zig" --rustc "$rustc" --xorriso "$xorriso"
```

Use the SHA-256 of each resulting `image.json` as its report hash. The
launch command verifies the report, ISO, and firmware. Use a new session
directory for the seed, then use the same directory for save and cold
readback. Each role has one attempt. QEMU has no network or monitor.

```sh
python3 -B sys-init/scripts/run-persistent-zsh.py seed "$work/session" \
  --image "$work/seed-image" --image-report-sha256 "$seed_report_sha" \
  --qemu "$qemu" --firmware "$firmware" --fixture "$seed_archive"
python3 -B sys-init/scripts/run-persistent-zsh.py save "$work/session" \
  --image "$work/note-image" --image-report-sha256 "$note_report_sha" \
  --qemu "$qemu" --firmware "$firmware"
python3 -B sys-init/scripts/run-persistent-zsh.py cold "$work/session" \
  --image "$work/note-image" --image-report-sha256 "$note_report_sha" \
  --qemu "$qemu" --firmware "$firmware" --manual
```

At the serial prompt, type the following commands to verify the saved
sample and exit cleanly. Omit `--manual` to run the same check with
prompt-driven input.

```zsh
v=$(</home/note); print -r -- "READ $? ${#v}"
x=aB3dE6gH9jK2mN5p; x=$x$x$x$x; x=$x$x$x$x
[[ $v == "$x" ]]; print -r -- "NOTE $? $$ $v"
exit 0
```

The startup failure check uses a separate blank disk and requires no
input. It confirms that storage failure leaves the shell unadmitted.
The result records guest engine cleanup and host stop separately.

```sh
python3 -B sys-init/scripts/run-persistent-zsh.py failure "$work/refusal" \
  --image "$work/note-image" --image-report-sha256 "$note_report_sha" \
  --qemu "$qemu" --firmware "$firmware"
```

Read `result.json` and the UART for each stage. If cleanup is unknown,
keep its outputs and stop. The launcher cannot reuse a failed stage or
its disk. Dispose of the owned generated images and disks after their
processes have stopped and the needed evidence is retained.
