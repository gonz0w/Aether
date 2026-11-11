#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the VT100 data and persisted executable for the R1 Zsh roles."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from bounded_tools import run_tool

ROOT = Path(__file__).resolve().parents[2]
FILESYSTEM = ROOT / 'userland/experiments/filesystem-service'
NCURSES_ARCHIVE = '355b4cbbed880b0381a04c46617b7656e362585d52e9cf84a67e2009b749ff11'
TERMINFO_SOURCE = '75673b421c25032306f7cdf26df57978c86ed9cf3d3fb16a6479233775f4f961'
TERMINFO = '512924dc4f0c9d70e6628d63615884aa93fad7d7fc7a9f62ba3536db24702dc1'
PROBE = '15d1a20d584543555420effcdb28fac2ca1f188dc2e1a88684e86f177a017de3'


def checked(raw, expected, label):
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f'{label} hash differs')
    return raw


def build(args):
    work = args.work.resolve()
    archive = args.ncurses.resolve(strict=True)
    if not archive.is_file() or archive.stat().st_size > 8 * 1024 * 1024:
        raise ValueError('expected the bounded ncurses source archive')
    checked(archive.read_bytes(), NCURSES_ARCHIVE, 'ncurses archive')
    tools = {name: str(getattr(args, name).resolve(strict=True))
             for name in ('rustc', 'linker', 'objcopy', 'tic')}
    work.mkdir(mode=0o700)
    (work / 'tmp').mkdir()
    environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work / 'tmp')}

    def run(label, argv):
        run_tool(argv, environment, work / (label + '.log'), timeout=30, cwd=work)

    with tarfile.open(archive, 'r:gz') as source:
        member = source.getmember('ncurses-6.6/misc/terminfo.src')
        if not member.isfile() or not 0 < member.size <= 2 * 1024 * 1024:
            raise ValueError('invalid terminfo source member')
        with source.extractfile(member) as stream:
            data = checked(stream.read(member.size + 1), TERMINFO_SOURCE, 'terminfo source')
    terminfo_source = work / 'terminfo.src'
    terminfo_source.write_bytes(data)
    database = work / 'db'
    run('tic', [tools['tic'], '-s', '-o', str(database), '-e', 'vt100', str(terminfo_source)])
    entries = [p for p in (database / 'v/vt100', database / '76/vt100') if p.is_file()]
    if len(entries) != 1:
        raise ValueError('expected exactly one VT100 database entry')
    (work / 'vt100').write_bytes(checked(entries[0].read_bytes(), TERMINFO, 'VT100 data'))

    symbols, probe = work / 'probe.symbols.elf', work / 'file-exec.elf'
    source = FILESYSTEM / 'zsh-file-exec-witness.rs'
    linker_script = FILESYSTEM / 'zsh-file-exec-witness.ld'
    run('rustc', [tools['rustc'], '--edition=2024', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn',
                  '--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=z',
                  '-Crelocation-model=static', '-Ccodegen-units=1', '-Cjump-tables=no',
                  '-Clto=fat', '-Cembed-bitcode=yes', '-Clinker=' + tools['linker'],
                  f'--remap-path-prefix={ROOT}=/src/aether', '-Clink-arg=-T' + str(linker_script),
                  '-Clink-arg=--gc-sections', '-Clink-arg=--build-id=none',
                  str(source), '-o', str(symbols)])
    run('objcopy', [tools['objcopy'], '--strip-sections', str(symbols), str(probe)])
    checked(probe.read_bytes(), PROBE, 'persisted executable')
    print(json.dumps({'terminfo_sha256': TERMINFO, 'probe_sha256': PROBE}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('work', 'ncurses', 'rustc', 'linker', 'objcopy', 'tic'):
        parser.add_argument('--' + name, type=Path, required=True)
    try:
        build(parser.parse_args())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Zsh asset build failed: {error}\n')


if __name__ == '__main__':
    main()
