#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check CLI manual coverage, curated examples and optional mandoc rendering."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, text=True,
                          timeout=60, cwd=ROOT, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-required', action='store_true')
    parser.add_argument('--binary-example', action='store_true',
                        help='run the compiler-dependent bytecount bundle example')
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix='pkg-manual-check-')).resolve()
    print(f'manual-check: retained_root={root}', flush=True)
    source = ROOT / 'man/pkg-mgr.1'
    manual = source.read_text()
    help_text = run([str(ROOT / 'bin/pkg-mgr'), '--help']).stdout
    commands = set()
    for line in help_text.split('Options (before COMMAND):')[0].splitlines():
        if line.startswith('  '):
            commands.update(part.strip().split()[0] for part in line.split(' | '))
    documented = set(re.findall(r'^\.It Cm ([a-z]+)', manual, re.M))
    options = set(re.findall(r'^  --([a-z-]+)', help_text, re.M))
    documented_options = set(re.findall(r'^\.It Fl -([a-z-]+)', manual, re.M))
    if not commands or commands != documented or options != documented_options:
        raise ValueError('manual/help command or option coverage mismatch')
    for section in ('NAME', 'SYNOPSIS', 'DESCRIPTION', 'EXIT STATUS',
                    'EXAMPLES', 'SEE ALSO', 'RECOVERY'):
        if '.Sh ' + section + '\n' not in manual:
            raise ValueError('missing manual section: ' + section)
    renderer = shutil.which('mandoc')
    lookup = shutil.which('man')
    if args.render_required and lookup is None:
        raise ValueError('BLOCKED: man is required for staged manual lookup')
    if args.render_required and renderer is None:
        raise ValueError('BLOCKED: mandoc is required for manual release checks')
    state_source = ROOT / 'man/pkg-state.5'
    state_manual = state_source.read_text()
    schema = (ROOT / 'mk/state-schema.awk').read_text()
    keys = re.search(r'key_count=split\("([^"]+)"', schema).group(1).split()
    evidence_section = state_manual.split('.Sh BUILD EVIDENCE\n')[1].split('.Sh IDENTIFIERS')[0]
    documented_keys = re.findall(r'^\.It Li ([a-z0-9_]+)$', evidence_section, re.M)
    if documented_keys != keys:
        raise ValueError('state manual evidence key/order coverage mismatch')
    for section in ('NAME', 'DESCRIPTION', 'RECORD FORMAT', 'WORLD AND DEPENDENCIES',
                    'COMPATIBILITY', 'EXAMPLES', 'FILES', 'SEE ALSO'):
        if '.Sh ' + section + '\n' not in state_manual:
            raise ValueError('missing state manual section: ' + section)
    binary_source = ROOT / 'man/pkg-binary.5'
    binary_manual = binary_source.read_text()
    artifact_keys = ['format', 'record_sha256', 'target_sha256', 'modes_sha256',
                     'dependencies_sha256', 'authenticity', 'service_activation']
    target_keys = ['format', 'host_os', 'host_arch', 'compiler_target', 'modes']
    for heading, end, expected in [('ARTIFACT DESCRIPTOR', 'TARGET RECORD', artifact_keys),
                                   ('TARGET RECORD', 'FILE AND DEPENDENCY TABLES', target_keys)]:
        section = binary_manual.split('.Sh ' + heading + '\n')[1].split('.Sh ' + end)[0]
        if re.findall(r'^\.It Li ([a-z0-9_]+)$', section, re.M) != expected:
            raise ValueError('binary manual field/order coverage mismatch')
    for section in ('NAME', 'DESCRIPTION', 'DIRECTORY LAYOUT', 'COMPATIBILITY',
                    'VALIDATION AND PUBLICATION', 'EXAMPLES', 'FILES', 'SEE ALSO'):
        if '.Sh ' + section + '\n' not in binary_manual:
            raise ValueError('missing binary manual section: ' + section)
    pages = (source, state_source, binary_source)
    if set((ROOT / 'man').glob('*.[1-9]')) != set(pages):
        raise ValueError('manual inventory has an unchecked page')
    # Curated counterparts of the manual's examples, never arbitrary code blocks.
    fixture = Path(tempfile.mkdtemp(prefix='.pkg-mgr-live-manual.', dir=ROOT))
    results = []
    for action in ('init-root', 'register'):
        result = run(['make', '-s', '-f', 'mk/pkg.mk', 'ROOT=' + str(fixture), action])
        results.append(result.stdout + result.stderr)
    cli = [str(ROOT / 'bin/pkg-mgr'), '--root', str(fixture)]
    listing = run(cli + ['list'])
    if 'hello-local' not in listing.stdout:
        raise ValueError('manual list example did not register hello-local')
    verified = run(cli + ['--plain', 'verify'])
    if 'Verified staged file contents' not in verified.stdout:
        raise ValueError('manual verify example did not report verification')
    files = run(cli + ['--format', 'tsv', 'files', 'hello-local'])
    if not files.stdout.strip():
        raise ValueError('manual files example returned no records')
    rejected = subprocess.run(cli + ['remove', 'hello-local'], cwd=ROOT,
                              capture_output=True, text=True, timeout=60)
    if rejected.returncode != 64 or rejected.stdout or not rejected.stderr:
        raise ValueError('manual unsupported-command example did not reject')
    world = fixture / 'state/world'
    world.write_text('hello-local\n')
    explicit = run(cli + ['--format', 'tsv', 'list'])
    if explicit.stdout != 'hello-local\t0.1\texplicit\n':
        raise ValueError('world example did not mark hello-local explicit')
    orphans = run(cli + ['--format', 'tsv', 'orphans'])
    if orphans.stdout != 'report\torphan-plan-v1\tnon-deleting\n':
        raise ValueError('world example unexpectedly reports orphans')
    try:
        world.write_text('hello-local\nhello-local\n')
        duplicate = subprocess.run(cli + ['--format', 'tsv', 'list'], cwd=ROOT,
                                   capture_output=True, text=True, timeout=60)
        if duplicate.returncode != 1 or duplicate.stdout or 'invalid or duplicate package name' not in duplicate.stderr:
            raise ValueError('duplicate world root did not fail without partial output')
    finally:
        world.write_text('hello-local\n')
    (root / 'state-examples.log').write_text(explicit.stdout + orphans.stdout + duplicate.stderr)
    (root / 'examples.log').write_text(''.join(results) + listing.stdout +
                                     verified.stdout + files.stdout + rejected.stderr)
    renderer = shutil.which('mandoc')
    if renderer:
        for page in pages:
            run([renderer, '-Tlint', '-Werror', str(page)])
            for width in (60, 80):
                rendered = run([renderer, '-Tascii', '-Owidth=' + str(width), str(page)])
                (root / f'{page.stem}.{width}.txt').write_text(rendered.stdout)
                plain = re.sub(r'.\x08', '', rendered.stdout)
                if any(len(line) > width for line in plain.splitlines()):
                    raise ValueError(f'{page.name} exceeds {width}-column rendering')
            rendered = run([renderer, '-Thtml', str(page)])
            (root / f'{page.stem}.html').write_text(rendered.stdout)
        print('PASS: three manuals linted and rendered as HTML and 60/80-column text')
    elif args.render_required:
        raise ValueError('BLOCKED: mandoc is required for manual release checks')
    else:
        print('NOT RUN: mandoc rendering; required before release')
    if lookup:
        manroot = root / 'share/man'
        environment = dict(os.environ, MANPAGER='cat', PAGER='cat', MANWIDTH='60')
        for page in pages:
            section = page.suffix[1:]
            directory = manroot / ('man' + section)
            directory.mkdir(parents=True, exist_ok=True)
            staged = directory / page.name
            shutil.copyfile(page, staged)
            found = run([lookup, '-w', '-M', str(manroot), section, page.stem], env=environment)
            if str(staged) not in found.stdout:
                raise ValueError('staged manual lookup selected a different page')
            displayed = run([lookup, '-M', str(manroot), section, page.stem], env=environment)
            if page.stem not in re.sub(r'.\x08', '', displayed.stdout):
                raise ValueError('staged manual display is empty or wrong')
            (root / f'{page.stem}.lookup.txt').write_text(found.stdout + displayed.stdout)
        print('PASS: three manuals found and displayed from private share/man layout')
    else:
        print('NOT RUN: staged manual lookup; man is required before release')
    binary_result = 'not-run: requires --binary-example and host compiler'
    if args.binary_example:
        example = run(['sh', 'tests/bytecount-integration.sh'])
        (root / 'binary-example.log').write_text(example.stdout + example.stderr)
        if 'PASS: bytecount source tamper rejection, parallel build, registration, binary import and imported execution' not in example.stdout:
            raise ValueError('binary manual example lacks completion marker')
        retained = Path(re.search(r'^retained_root=(.+)$', example.stdout, re.M).group(1))
        bundle = retained / 'binaries/bytecount'
        expected_files = {'artifact.kv', 'package.tsv', 'target.kv', 'modes.tsv', 'dependencies.tsv', 'files'}
        if {p.name for p in bundle.iterdir()} != expected_files:
            raise ValueError('binary example differs from documented directory inventory')
        artifact = (bundle / 'artifact.kv').read_text().splitlines()
        target = (bundle / 'target.kv').read_text().splitlines()
        if [row.split('=', 1)[0] for row in artifact] != artifact_keys or [row.split('=', 1)[0] for row in target] != target_keys:
            raise ValueError('actual bundle keys differ from binary manual')
        for key, name in [('record_sha256', 'package.tsv'), ('target_sha256', 'target.kv'),
                          ('modes_sha256', 'modes.tsv'), ('dependencies_sha256', 'dependencies.tsv')]:
            expected = dict(row.split('=', 1) for row in artifact)[key]
            if hashlib.sha256((bundle / name).read_bytes()).hexdigest() != expected:
                raise ValueError('documented descriptor digest binding fails')
        for name in ('artifact.kv', 'target.kv'):
            shutil.copyfile(bundle / name, root / name)
        binary_result = 'pass: actual bundle inventory, keys and digest bindings match'
        print('PASS: compiler-dependent binary manual example and actual bundle schema')
    else:
        print('NOT RUN: binary compiler example; use --binary-example before release')
    (root / 'result.json').write_text(json.dumps({
        'binary_manual_sha256': hashlib.sha256(binary_source.read_bytes()).hexdigest(),
        'binary_example': binary_result,
        'state_manual_sha256': hashlib.sha256(state_source.read_bytes()).hexdigest(),
        'state_schema_sha256': hashlib.sha256((ROOT / 'mk/state-schema.awk').read_bytes()).hexdigest(),
        'evidence_keys': keys,
        'manual_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'cli_sha256': hashlib.sha256((ROOT / 'bin/pkg-mgr').read_bytes()).hexdigest(),
        'fixture_root': str(fixture),
        'commands': sorted(commands), 'options': sorted(options),
        'lookup_tool': lookup,
        'lookup_tool_sha256': hashlib.sha256(Path(lookup).read_bytes()).hexdigest() if lookup else None,
        'renderer': renderer,
        'renderer_sha256': hashlib.sha256(Path(renderer).read_bytes()).hexdigest() if renderer else None,
        'platform': platform.platform(), 'examples': 'pass',
        'scope': 'host source manual; no packaged target or independent reader approval',
    }, indent=2) + '\n')
    print(f'PASS: {len(commands)} commands, {len(options)} options, {len(keys)} evidence keys and curated manual examples')


if __name__ == '__main__':
    main()
