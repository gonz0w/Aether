#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Actual-source host SHA read-error witness; no native execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_tools import run_tool


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('archive', 'generated', 'tools-lock', 'work'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--pristine-only', action='store_true')
    args = parser.parse_args()
    work = args.work.resolve()
    if not work.is_relative_to(ROOT / 'userland/build'):
        parser.error('work must be fresh under userland/build')
    work.mkdir(mode=0o700)
    (work / 'tmp').mkdir()
    report = dict(scope='host actual-source read-fault witness; not native runtime evidence', commands=[], cases=[])
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work / 'tmp')}

    def save():
        (work / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(argv, cwd, selected_env, expected=0):
        argv = list(map(str, argv))
        label = f'{len(report["commands"]):03d}-{Path(argv[0]).name}'
        row = dict(argv=argv, cwd=str(cwd), expected=expected, log=label + '.log')
        report['commands'].append(row)
        save()
        try:
            raw = run_tool(argv, selected_env, work / row['log'], timeout=90, cwd=cwd)
            status = 0
        except subprocess.CalledProcessError as error:
            status = error.returncode
            raw = (work / row['log']).read_bytes()
        row['status'] = status
        save()
        if status != expected:
            raise ValueError(f'{label} returned {status}, expected {expected}')
        return raw

    try:
        source = json.loads((HERE.parent / 'toybox-reference/source.lock.json').read_text())
        if sha(args.archive) != source['sha256']:
            raise ValueError('source archive changed')
        tool = json.loads(args.tools_lock.read_text())['tools']['clang']
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('compiler changed')
        generated = args.generated.resolve()
        if '#define CFG_SHA256SUM 1' not in (generated / 'config.h').read_text() or '#define CFG_TOYBOX_LIBCRYPTO 0' not in (generated / 'config.h').read_text():
            raise ValueError('selected builtin SHA generated config required')
        report.update(source=source, compiler=tool,
                      generated_inputs={p.name: sha(p) for p in generated.iterdir() if p.is_file()},
                      harness_sha256=sha(HERE / 'read-fault.c'), checker_sha256=sha(Path(__file__)))
        sdk = run(['/usr/bin/xcrun', '--show-sdk-path'], work, env).decode().splitlines()[-1]
        if not Path(sdk).is_dir():
            raise ValueError('host SDK path unavailable')
        for variant in ('pristine',) if args.pristine_only else ('pristine', 'patched'):
            case = work / variant
            case.mkdir()
            with tarfile.open(args.archive) as archive:
                archive.extractall(case, filter='data')
            tree = case / ('toybox-' + source['version'])
            (tree / 'generated').symlink_to(generated)
            if variant == 'patched':
                spec = importlib.util.spec_from_file_location('hash_build', HERE / 'build.py')
                builder = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(builder)
                report['patch'] = builder.apply_hash_patch(tree, run)
            common = [tool['path'], '--no-default-config', '--target=arm64-apple-macos', '-isysroot', sdk,
                      '-Oz', '-ffunction-sections', '-fdata-sections', '-funsigned-char', '-fno-strict-aliasing',
                      '-Werror=implicit-function-declaration', '-Wno-pointer-sign', '-Wno-string-plus-int',
                      '-Wno-deprecated-declarations', '-Wno-invalid-source-encoding', '-I' + str(tree),
                      '-DTOYBOX_VERSION="0.8.14"']
            sources = [tree / 'main.c', tree / 'toys/lsb/md5sum.c', *sorted((tree / 'lib').glob('*.c'))]
            objects = []
            for number, path in enumerate(sources):
                obj = case / f'{number}.o'
                flags = ['-Dread=aether_hash_test_read'] if path.name in ('hash.c', 'xwrap.c') else []
                run([*common, *flags, '-c', path, '-o', obj], case, env)
                objects.append(obj)
            double = case / 'read-fault.o'
            run([*common, '-std=c17', '-Wall', '-Wextra', '-Werror', '-c', HERE / 'read-fault.c', '-o', double], case, env)
            binary = case / 'sha256sum'
            run([*common, '-Wl,-dead_strip', *objects, double, '-o', binary], case, env)
            report[variant + '_host_binary_sha256'] = sha(binary)
            for name, data, fault in [('abcdef', b'abcdef', ''), ('empty', b'', ''),
                                      ('initial-eio', b'abcdef', 'initial-eio'),
                                      ('partial-eio', b'abcdef', 'partial-eio')]:
                input_path = case / name
                input_path.write_bytes(data)
                selected = dict(env, AETHER_HASH_READ_FAULT=fault)
                # Separate stdout/stderr so diagnostics cannot impersonate a digest.
                command = [str(binary), str(input_path)]
                stdout, stderr = case / (name + '.stdout'), case / (name + '.stderr')
                with stdout.open('wb') as out, stderr.open('wb') as err:
                    completed = subprocess.run(command, env=selected, stdout=out, stderr=err, timeout=10)
                expected_error = variant == 'patched' and bool(fault)
                actual = stdout.read_bytes()
                if expected_error:
                    if completed.returncode == 0 or actual or b'xread:' not in stderr.read_bytes():
                        raise ValueError('read error completed a digest or lost failure: ' + name)
                else:
                    digested = b'' if fault == 'initial-eio' else b'abc' if fault == 'partial-eio' else data
                    expected = hashlib.sha256(digested).hexdigest().encode() + b'  ' + str(input_path).encode() + b'\n'
                    if completed.returncode != 0 or actual != expected or stderr.read_bytes():
                        raise ValueError('actual source digest/output/status mismatch: ' + name)
                report['cases'].append(dict(variant=variant, name=name, argv=command, status=completed.returncode,
                                            stdout=actual.decode(), stderr=stderr.read_text(),
                                            observation='truthful read failure; no digest' if expected_error else
                                            'pristine false-success' if fault else 'correct digest'))
                save()
        report['status'] = 'passed'
        save()
    except Exception as error:
        report.update(status='failed', error=type(error).__name__ + ': ' + str(error))
        save()
        raise
    print(json.dumps(report['cases'], indent=2))


if __name__ == '__main__':
    main()
