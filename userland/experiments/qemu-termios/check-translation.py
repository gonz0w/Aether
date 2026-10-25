#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Bounded host QEMU CMSPAR translation test; run from repository root."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import sys
import tarfile
import tempfile

ROOT = Path.cwd()
HERE = ROOT / 'experiments/qemu-termios'
PROCESS = runpy.run_path(str(ROOT / 'experiments/command-runner/process.py'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='qemu-translation-', dir=ROOT / 'build'))
    report = {'status': 'incomplete', 'work': str(work), 'commands': [],
              'scope': 'host selected translation functions; emulator NOT BUILT',
              'python': sys.version}

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    def command(label, args, expected=0):
        result = PROCESS['run'](args, cwd=work, env=PROCESS['clean_env'](work),
                                work=work, label=label, timeout=30)
        report['commands'].append(result.record)
        save()
        if not result.record['complete'] or result.returncode != expected:
            raise RuntimeError(label + ': unexpected outcome')

    save()
    try:
        lock = json.loads((HERE / 'source.lock.json').read_text())
        archive = ROOT / lock['archive']
        if sha(archive) != lock['sha256']:
            raise RuntimeError('source archive drift')
        build_pin = json.loads((HERE / 'build-inputs.lock.json').read_text())
        for name, digest in build_pin['files'].items():
            if sha(Path(build_pin['root']) / name) != digest:
                raise RuntimeError('build input drift: ' + name)
        names = ['linux-user/syscall.c', 'linux-user/thunk.c', 'include/user/thunk.h',
                 'linux-user/generic/termbits.h', 'linux-user/x86_64/termbits.h',
                 'COPYING', 'COPYING.LIB']
        with tarfile.open(archive, 'r|xz') as tar:
            for member in tar:
                rel = member.name.removeprefix('qemu-10.0.11/')
                if rel in names:
                    if not member.isfile():
                        raise RuntimeError('unexpected source type')
                    dest = work / 'original' / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(tar.extractfile(member).read())
        report['inputs'] = {name: sha(work / 'original' / name) for name in names}
        original = (work / 'original/linux-user/syscall.c').read_text()
        anchor = '\t{ TARGET_CRTSCTS, TARGET_CRTSCTS, CRTSCTS, CRTSCTS },\n'
        if original.count(anchor) != 1 or 'TARGET_CMSPAR, TARGET_CMSPAR' in original:
            raise RuntimeError('patch anchor drift')
        row = ('#if defined(TARGET_CMSPAR) && defined(CMSPAR)\n'
               '        { TARGET_CMSPAR, TARGET_CMSPAR, CMSPAR, CMSPAR },\n'
               '#endif\n')
        patched = original.replace(anchor, anchor + row)
        patch = ''.join(difflib.unified_diff(original.splitlines(True),
                                            patched.splitlines(True),
                                            fromfile='a/linux-user/syscall.c',
                                            tofile='b/linux-user/syscall.c'))
        (work / 'cmspar.patch').write_text(patch)
        thunk = (work / 'original/linux-user/thunk.c').read_text()
        header = (work / 'original/include/user/thunk.h').read_text()
        functions = thunk[thunk.index('unsigned int target_to_host_bitmask_len('):
                          thunk.index('int thunk_type_size_array(')]
        struct = re.search(r'typedef struct bitmask_transtbl \{.*?\} bitmask_transtbl;',
                           header, re.S).group()
        # Keep upstream notices with the derived test translation units.
        notices = original[:original.index('*/') + 2] + '\n' + thunk[:thunk.index('*/') + 2]
        shutil.copy2(work / 'original/linux-user/generic/termbits.h', work / 'termbits.h')
        pin = json.loads((ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json').read_text())['tools']['clang']
        if sha(Path(pin['path'])) != pin['sha256']:
            raise RuntimeError('compiler drift')
        report['compiler'] = pin
        sdk = Path('/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk')
        report['host_sdk'] = {'path': str(sdk), 'selected_files': {
            name: sha(sdk / name) for name in ('SDKSettings.json', 'usr/lib/libSystem.tbd')
        }, 'scope': 'selected link inputs; not a complete host SDK closure'}
        control = (HERE / 'translation-control.c').read_text()
        aliases = ['CSIZE', 'CS5', 'CS6', 'CS7', 'CS8', 'CSTOPB', 'CREAD',
                   'PARENB', 'PARODD', 'HUPCL', 'CLOCAL', 'CRTSCTS']
        for name, source, support, expected in [
                ('baseline', original, 1, 20), ('patched', patched, 1, 0),
                ('missing-host', patched, 0, 0), ('missing-target', patched, 0, 0),
                ('wrong-bit', patched.replace('CMSPAR, CMSPAR },', 'CLOCAL, CLOCAL },'), 1, 20)]:
            table = source[source.index('\t{ TARGET_CSIZE,'):source.index('static const bitmask_transtbl lflag_tbl')]
            definitions = '#include <stddef.h>\n#include "termbits.h"\n'
            definitions += '\n'.join('#define ' + a + ' TARGET_' + a for a in aliases)
            definitions += '\n#define MODEL_HOST_CMSPAR 0x10000000u\n'
            definitions += '#define MODEL_TARGET_CMSPAR 0x40000000u\n'
            if name != 'missing-host':
                definitions += '#define CMSPAR MODEL_HOST_CMSPAR\n'
            if name == 'missing-target':
                definitions += '#undef TARGET_CMSPAR\n'
            else:
                definitions += '_Static_assert(TARGET_CMSPAR == MODEL_TARGET_CMSPAR, "target pin");\n'
            text = (notices + '\n' + definitions + '\n' + struct + '\n' + functions +
                    '\nstatic const bitmask_transtbl cflag_tbl[] = {\n' + table +
                    '\n#define EXPECT_SUPPORT ' + str(support) + '\n' + control)
            path = work / (name + '.c')
            path.write_text(text)
            command(name + '-compile', [pin['path'], '--no-default-config',
                    '-isysroot', str(sdk), '-std=c17',
                    '-O2', '-Wall', '-Wextra', '-Werror', str(path), '-o', str(work / name)])
            command(name + '-run', [str(work / name)], expected)
        report['sources'] = {str(p): sha(p) for p in [Path(__file__), HERE / 'translation-control.c',
                             HERE / 'TRANSLATION-PLAN.md', HERE / 'source.lock.json',
                             HERE / 'build-inputs.lock.json', ROOT / 'experiments/command-runner/process.py']}
        report['artifacts'] = {p.name: sha(p) for p in work.iterdir() if p.is_file() and p.name != 'summary.json'}
        report['verified_build_inputs'] = len(build_pin['files'])
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
        save()
        return 1
    save()
    print('Host translation controls pass; emulator NOT BUILT. Evidence: ' + str(work))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
