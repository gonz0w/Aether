#!/usr/bin/env python3
"""Build the sys-init-owned, no_std Aether lifecycle v1 client."""
import argparse
from pathlib import Path
import struct
import subprocess
from bounded_tools import run_recorded

ROOT = Path(__file__).resolve().parents[1]

def build(output, variant):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    compiler = ['rustc', '+1.98.0']
    version = run_recorded(compiler + ['--version'], output / (variant + '-version.log'), __file__).decode().strip()
    if version.split()[1] != '1.98.0':
        raise RuntimeError('Rust 1.98.0 required')
    raw = output / (variant + '.raw')
    command = compiler + ['--edition=2024', '--target=x86_64-unknown-none',
        '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
        '-C', 'link-arg=-T' + str(ROOT / 'prototypes/aether-lifecycle/linker.ld'),
        '-C', 'link-arg=--oformat=binary', '--check-cfg=cfg(fault_entry)',
        '--check-cfg=cfg(wrong_detail)', str(ROOT / 'prototypes/aether-lifecycle/main.rs'),
        '-o', str(raw)]
    if variant != 'pass':
        command += ['--cfg', variant]
    run_recorded(command, output / (variant + '-build.log'), __file__)
    code = raw.read_bytes()
    if not 0 < len(code) <= 4096:
        raise RuntimeError('client must fit one immutable page')
    envelope = output / (variant + '.bin')
    envelope.write_bytes(struct.pack('<8sIIQII', b'AELIFE01', 1, 1, 0x400000, len(code), 0) + code)
    print(f'{envelope}: {len(code)} code bytes, {version}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--variant', choices=['pass', 'fault_entry', 'wrong_detail'], default='pass')
    args = parser.parse_args()
    build(args.output, args.variant)
