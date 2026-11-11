# Build the persistent Zsh inputs from source

The R1 developer build uses the seed and note roles in the
[persistent serial recipe](PERSISTENT-ZSH.md). It builds the guarded
musl SDK, selected UTC runtime, OpenZFS engine, Rust Owner, and Zsh
applications from pinned source inputs. The supplied seals remain
available through the same image builder.

Prepare Zig 0.16.0, QEMU 11.1.1, xorriso 1.5.8.pl02, LLVM/LLD 21.1.8,
ncurses 6.6 tools, and the Rust 1.98.0 toolchain with
`x86_64-unknown-none` support. The qualified build runs on the host
toolchain whose executable and target library hashes are in
[`r1-zsh-tool-pins.json`](../scripts/r1-zsh-tool-pins.json).
Pass absolute paths for the installed tools. The build scripts target Aether.

Fetch the pinned Limine and firmware with `python3 scripts/deps.py`.
Acquire source inputs with the command below. Its output is the offline
archive directory used by the build. Zsh
and ncurses must match the SHA-256 and signing fingerprints in the
[Zsh source manifest](../../userland/docs/zsh-consumer-v1.json).
The ncurses signature is also available from the [maintainer mirror](https://invisible-mirror.net/archives/ncurses/).
Use the pinned musl 1.2.6 archive, OpenZFS commit
`71a9f9578616a90c3c14bb59629fb4d31bfd68d1`, zlib 1.3.2,
and libtirpc 1.3.6. The support build checks all three archive
identities before extraction. The OpenZFS seed fixture is the
[test pool from the pinned commit](https://github.com/openzfs/zfs/blob/71a9f9578616a90c3c14bb59629fb4d31bfd68d1/tests/zfs-tests/tests/functional/compression/testpool_zstd.tar.gz).

```sh
python3 -B sys-init/scripts/fetch-r1-zsh-sources.py --output "$sources" \
  --curl "$curl" --gpg "$gpg" --gpgv "$gpgv"
```

From the repository root, create a fresh directory under `userland/build`
and set `work` to its absolute path. Set `sources` to the offline
archive directory. Set the following variables to the pinned tool paths:
`llvm_bin`, `rust_root`, `lld`, `make_tool`, `zig`, `xorriso`, and `tic`.

```sh
python3 -B sys-init/scripts/prepare-r1-zsh-toolchain.py \
  --llvm-bin "$llvm_bin" --rust-root "$rust_root" --lld "$lld" \
  --make "$make_tool" --zig "$zig" --xorriso "$xorriso" --tic "$tic" \
  --output "$work/tools.json"

python3 -B userland/experiments/native-c/build.py --io --source-build \
  --tools-lock "$work/tools.json" --musl-archive "$sources/musl-1.2.6.tar.gz" \
  --output "$work/sdk"

python3 -B userland/experiments/native-service-runtime/build.py \
  --sdk "$work/sdk" --output "$work/runtime" --tools-lock "$work/tools.json" \
  --musl-archive "$sources/musl-1.2.6.tar.gz"

python3 -B scripts/r1_openzfs_support.py --work "$work/support" \
  --clang "$llvm_bin/clang" \
  --clang-sha256 625165a3accc542dafef0264b5bbd18721b8e765c7ec819742ec7d7afd2491f6 \
  --sdk "$work/sdk/stage/usr" --openzfs "$sources/openzfs-71a9f.tar.gz" \
  --zlib "$sources/zlib-1.3.2.tar.gz" --tirpc "$sources/libtirpc-1.3.6.tar.bz2"

python3 -B sys-init/scripts/build-r1-zsh-assets.py --work "$work/assets" \
  --ncurses "$sources/ncurses-6.6.tar.gz" --tic "$tic" \
  --rustc "$rust_root/bin/rustc" --linker "$lld" --objcopy "$llvm_bin/llvm-objcopy"
```

Build each engine and Owner under the same work directory.

```sh
for role in seed note; do
  python3 -B scripts/r1_openzfs_engine.py "$role" --work "$work/engine-$role" \
    --support "$work/support" --sdk "$work/sdk/stage/usr" \
    --runtime "$work/runtime" --toolchain "$work/tools.json"
  python3 -B sys-init/scripts/build-r1-zsh-owner.py "$role" --work "$work/owner-$role" \
    --rustc "$rust_root/bin/rustc" --linker "$lld" \
    --objcopy "$llvm_bin/llvm-objcopy" --objdump "$llvm_bin/llvm-objdump" \
    --terminfo "$work/assets/vt100" --probe "$work/assets/file-exec.elf"
done
```

Build Zsh and the boot-image helpers against the fresh SDK.

```sh
python3 -B userland/experiments/filesystem-service/r1-zsh-source.py \
  --sdk "$work/sdk" --sources "$sources" --tools-lock "$work/tools.json" \
  --out-dir "$work/apps"

for role in seed note; do
  mkdir "$work/inputs-$role"
  cp "$work/engine-$role/filesystem.elf" "$work/inputs-$role/filesystem.elf"
  cp "$work/owner-$role/owner.bin" "$work/inputs-$role/owner.bin"
  cp "$work/apps/$role-zsh.elf" "$work/inputs-$role/zsh.elf"
  cp "$work/apps/$role-helper.elf" "$work/inputs-$role/helper.elf"
  python3 -B sys-init/scripts/build-persistent-zsh.py "$role" "$work/image-$role" \
    --source-inputs "$work/inputs-$role" --zig "$zig" \
    --rustc "$rust_root/bin/rustc" --xorriso "$xorriso"
done
```

The image builder checks each role's input hashes and complete envelope
against the artifact lock, then runs the kernel loader's geometry checks.
For the seed launch pass `"$sources/testpool_zstd.tar.gz"` as the fixture.
Use the same seed, save and cold commands from the
[persistent serial recipe](PERSISTENT-ZSH.md) with these images and
their image report hashes.
