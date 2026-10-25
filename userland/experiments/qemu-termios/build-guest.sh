#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
set -eu
inputs=$1
output=$2
cd "$output"
# Prevent service startup by Debian maintainer scripts inside this build-only root.
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
mkdir -p package-cache/partial
cp "$inputs"/debs/*.deb package-cache/
DEBIAN_FRONTEND=noninteractive apt-get --no-download --yes --no-install-recommends \
    -o APT::Sandbox::User=root -o Dir::Cache::archives="$output/package-cache" install "$inputs"/debs/*.deb > packages.stdout 2> packages.stderr
dpkg-query -W > installed-packages.txt
/usr/bin/clang-19 --version > compiler.txt
/usr/bin/meson --version > meson.txt
/usr/bin/ninja --version > ninja.txt
/usr/bin/python3 --version > python.txt
uname -a > kernel.txt
/usr/bin/python3 "$inputs/extract-source.py" "$inputs/qemu.tar.xz"
mv qemu-10.0.11 source
sha256sum source/linux-user/syscall.c > baseline-source.sha256
mkdir baseline
cd baseline
../source/configure --target-list=x86_64-linux-user --without-default-features \
    --disable-system --disable-tools --disable-docs --disable-guest-agent \
    --disable-download --cc=/usr/bin/clang-19 --cxx=/usr/bin/clang++-19 \
    --python=/usr/bin/python3 > configure.stdout 2> configure.stderr
ninja -j2 qemu-x86_64 > build.stdout 2> build.stderr
./qemu-x86_64 --version > version.txt
sha256sum qemu-x86_64 > binary.sha256
cd ../source
/usr/bin/python3 "$inputs/apply-cmspar.py" linux-user/syscall.c "$inputs/cmspar.patch" \
    > ../patch.stdout 2> ../patch.stderr
sha256sum linux-user/syscall.c > ../patched-source.sha256
cd ..
mkdir patched
cd patched
../source/configure --target-list=x86_64-linux-user --without-default-features \
    --disable-system --disable-tools --disable-docs --disable-guest-agent \
    --disable-download --cc=/usr/bin/clang-19 --cxx=/usr/bin/clang++-19 \
    --python=/usr/bin/python3 > configure.stdout 2> configure.stderr
ninja -j2 qemu-x86_64 > build.stdout 2> build.stderr
./qemu-x86_64 --version > version.txt
sha256sum qemu-x86_64 > binary.sha256
printf 'QEMU unpatched and patched builds complete\n'
