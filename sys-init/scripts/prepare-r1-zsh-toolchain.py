#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Resolve the pinned R1 source-build tools from explicit host directories."""
import argparse
import hashlib
import json
from pathlib import Path

PINS = Path(__file__).with_name('r1-zsh-tool-pins.json')
LLVM = ('clang', 'ar', 'ranlib', 'nm', 'readelf', 'objcopy', 'objdump')
RUST = ('rustc', 'rustfmt', 'clippy-driver')
ALIASES = {name: 'llvm-' + name for name in LLVM if name != 'clang'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare(args):
    pins = json.loads(PINS.read_text())
    tools = {name: args.llvm_bin / ALIASES.get(name, name) for name in LLVM
             if name in pins['tools']}
    tools.update({name: args.rust_root / 'bin' / name for name in RUST
                  if name in pins['tools']})
    for name in pins['tools'].keys() - tools.keys():
        tools[name] = getattr(args, name)
    receipt = {'tools': {}, 'rust_native_libraries': {}}
    for name, path in tools.items():
        resolved = path.absolute()
        actual = sha(resolved)
        if actual != pins['tools'][name]:
            raise ValueError('pinned tool differs: ' + name)
        receipt['tools'][name] = {'path': str(resolved), 'sha256': actual}
    for name, expected in pins['rust_native_libraries'].items():
        path = args.rust_root.absolute() / 'lib/rustlib/x86_64-unknown-none/lib' / name
        if sha(path) != expected:
            raise ValueError('pinned Rust target library differs: ' + name)
        receipt['rust_native_libraries'][str(path)] = expected
    with args.output.open('x') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('llvm-bin', 'rust-root', 'lld', 'make', 'zig', 'xorriso', 'tic', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    try:
        prepare(parser.parse_args())
    except (OSError, ValueError, KeyError, AttributeError) as error:
        parser.exit(1, f'Toolchain verification failed: {error}\n')


if __name__ == '__main__':
    main()
