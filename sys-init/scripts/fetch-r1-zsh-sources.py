#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Acquire pinned R1 Zsh source archives before running the offline build."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from bounded_tools import run_tool

ROOT = Path(__file__).resolve().parents[2]
OPENZFS_COMMIT = '71a9f9578616a90c3c14bb59629fb4d31bfd68d1'
ARCHIVES = {
    'musl-1.2.6.tar.gz': (
        'https://musl.libc.org/releases/musl-1.2.6.tar.gz',
        'd585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a'),
    'openzfs-71a9f.tar.gz': (
        'https://codeload.github.com/openzfs/zfs/tar.gz/' + OPENZFS_COMMIT,
        'bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8'),
    'testpool_zstd.tar.gz': (
        'https://raw.githubusercontent.com/openzfs/zfs/' + OPENZFS_COMMIT
        + '/tests/zfs-tests/tests/functional/compression/testpool_zstd.tar.gz',
        'b5a4609e8b3575ca6ab9b7ed3b5db3b2967ca2f026df8b3ece901a6cfa513bcc'),
    'zlib-1.3.2.tar.gz': (
        'https://zlib.net/fossils/zlib-1.3.2.tar.gz',
        'bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16'),
    'libtirpc-1.3.6.tar.bz2': (
        'https://downloads.sourceforge.net/project/libtirpc/libtirpc/1.3.6/libtirpc-1.3.6.tar.bz2',
        'bbd26a8f0df5690a62a47f6aa30f797f3ef8d02560d1bc449a83066b5a1d3508'),
}
NCURSES_MIRROR = 'https://invisible-mirror.net/archives/ncurses/'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fetch(args):
    output = args.output.resolve()
    output.mkdir(mode=0o700)
    manifest = json.loads((ROOT / 'userland/docs/zsh-consumer-v1.json').read_text())
    tools = {name: str(getattr(args, name).resolve(strict=True)) for name in ('curl', 'gpg', 'gpgv')}
    receipts = {}
    with tempfile.TemporaryDirectory(prefix='verify-', dir=output) as temporary:
        work = Path(temporary)
        environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work)}

        def run(label, command):
            return run_tool(command, environment, work / (label + '.log'), timeout=35, cwd=work)

        def download(name, url, limit=48 * 1024 * 1024):
            path = work / name
            run(name, [tools['curl'], '--fail', '--silent', '--show-error', '--location',
                       '--proto', '=https', '--max-time', '30', '--max-filesize', str(limit),
                       '--output', str(path), url])
            return path

        for source in manifest['sources']:
            name = source['archive'].rsplit('/', 1)[-1]
            archive_url, signature_url = source['archive'], source['signature']
            key_url = source['key'].replace('@', '%40')
            if source['name'] == 'ncurses':
                archive_url, signature_url = NCURSES_MIRROR + name, NCURSES_MIRROR + name + '.asc'
                key_url = key_url.replace('https://invisible-island.net/', 'https://invisible-mirror.net/', 1)
            archive = download(name, archive_url)
            if sha(archive) != source['sha256']:
                raise ValueError('source archive hash differs: ' + name)
            signature = download(name + '.sig', signature_url, 1024 * 1024)
            key = download(name + '.key', key_url, 1024 * 1024)
            ring = work / (name + '.gpg')
            run(name + '-key', [tools['gpg'], '--homedir', str(work), '--batch', '--no-options',
                              '--no-autostart', '--dearmor', '--output', str(ring), str(key)])
            status = run(name + '-verify', [tools['gpgv'], '--homedir', str(work), '--keyring', str(ring),
                                           '--status-fd', '1', str(signature), str(archive)]).decode()
            valid = [row.split()[-1] for row in status.splitlines() if row.startswith('[GNUPG:] VALIDSIG ')]
            if valid != [source['primary_signer']]:
                raise ValueError('unexpected source signer: ' + name)
            archive.rename(output / name)
            receipts[name] = dict(url=archive_url, sha256=source['sha256'],
                                  signature_url=signature_url, key_url=key_url, primary_signer=valid[0])
        for name, (url, expected) in ARCHIVES.items():
            path = download(name, url)
            if sha(path) != expected:
                raise ValueError('source archive hash differs: ' + name)
            path.rename(output / name)
            receipts[name] = dict(url=url, sha256=expected)
    (output / 'sources.json').write_text(json.dumps(receipts, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'curl', 'gpg', 'gpgv'):
        parser.add_argument('--' + name, required=True, type=Path)
    try:
        fetch(parser.parse_args())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f'R1 source acquisition stopped: {error}\n')


if __name__ == '__main__':
    main()
