#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build an explicit private service-runtime supplement; Python3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import types

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def display(value):
    return ''.join('\\x%02x' % ord(c) if ord(c) < 32 or ord(c) == 127 else c
                   for c in str(value))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        super().error(display(message))


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def build(sdk, output):
    sdk, output = sdk.resolve(), output.resolve()
    need(output.is_relative_to(ROOT / 'build') and not output.exists(),
         'output must be fresh under build')
    output.mkdir()
    helper = ROOT / 'experiments/command-runner/process.py'
    need(sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e',
         'owned process helper pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
    lock = json.loads((sdk / 'tools.lock.json').read_text())
    tools = lock['tools']
    for name in ('clang', 'lld', 'ar', 'nm'):
        need(sha(Path(tools[name]['path'])) == tools[name]['sha256'], name)
    seal = sdk / 'SHA256SUMS'
    need(sha(seal) == 'f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc',
         'selected guarded SDK seal')
    sealed = {}
    for line in seal.read_text().splitlines():
        digest, name = line.split('  ', 1)
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts
             and name not in sealed, 'SDK seal path')
        path = sdk / relative
        need(path.is_file() and not path.is_symlink() and sha(path) == digest,
             'SDK member ' + name)
        sealed[name] = digest
    receipt_path = sdk / 'evidence.json'
    if not receipt_path.exists():
        receipt_path = sdk / 'build-evidence.json'
    receipt = json.loads(receipt_path.read_text())
    need(sha(sdk / 'stage/usr/lib/libc.a') == receipt['libc_archive_sha256'],
         'guarded base libc')
    need(receipt.get('libc_patches'), 'strict/error guards required')
    archive = sdk / 'musl-1.2.6.tar.gz'
    need(sha(archive) == receipt['source_sha256'], 'upstream source')
    selection = {
        'pthread': 'src/thread/pthread_create.c',
        'join': 'src/thread/pthread_join.c',
        'timedwait': 'src/thread/__timedwait.c',
        'cp': 'src/thread/__syscall_cp.c',
        'vm': 'src/thread/vmlock.c',
        'block': 'src/signal/block.c',
        'mmap': 'src/mman/mmap.c',
        'mprotect': 'src/mman/mprotect.c',
        'munmap': 'src/mman/munmap.c',
        'wait': 'src/thread/__wait.c',
        'lock': 'src/thread/__lock.c',
        'sleep': 'src/time/clock_nanosleep.c',
        'nanosleep': 'src/time/nanosleep.c',
    }
    for stem in ('pthread_rwlock_rdlock', 'pthread_rwlock_wrlock',
                 'pthread_rwlock_tryrdlock', 'pthread_rwlock_trywrlock',
                 'pthread_rwlock_timedrdlock', 'pthread_rwlock_timedwrlock',
                 'pthread_rwlock_unlock', 'pthread_cond_wait',
                 'pthread_cond_timedwait', 'pthread_cond_signal',
                 'pthread_cond_broadcast', 'pthread_mutex_lock',
                 'pthread_mutex_trylock', 'pthread_mutex_timedlock',
                 'pthread_mutex_unlock', 'pthread_key_create',
                 'pthread_setspecific', 'pthread_getspecific'):
        selection[stem] = 'src/thread/' + stem + '.c'
    headers = output / 'musl'
    originals = {}
    with tarfile.open(archive) as source:
        for member in source:
            relative = member.name.removeprefix('musl-1.2.6/')
            path = Path(relative)
            need(not path.is_absolute() and '..' not in path.parts, 'upstream path')
            wanted = relative == 'COPYRIGHT' or relative in selection.values()
            wanted |= relative.endswith('.h') and relative.startswith(
                ('src/internal/', 'src/include/', 'arch/x86_64/',
                 'arch/generic/', 'include/'))
            if wanted and member.isfile():
                target = headers / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.extractfile(member).read())
                originals[relative] = sha(target)
    patches = []
    for relative, old, new in [
        ('src/thread/pthread_create.c',
         '\tself = __pthread_self();\n\tif (!libc.threaded)',
         '\tself = __pthread_self();\n'
         '\textern int aether_pthread_admit(const void *);\n'
         '\tint admission = aether_pthread_admit(attrp);\n'
         '\tif (admission) return admission;\n'
         '\tunsigned long native_mask = 0;\n'
         '\tint native_error = __syscall(SYS_rt_sigprocmask, SIG_SETMASK, 0, &native_mask, _NSIG/8);\n'
         '\tif (native_error < 0) return -native_error;\n'
         '\tif (!libc.threaded)'),
        ('src/thread/__timedwait.c', '\tif (at) {\n',
         '\tif (at) {\n'
         '\t\textern int aether_libc_timedwait(volatile int *, int, clockid_t, const struct timespec *, int);\n'
         '\t\treturn aether_libc_timedwait(addr, val, clk, at, !!priv);\n'
         '\t}\n\tif (at) {\n'),
    ]:
        target = headers / relative
        original = target.read_text()
        need(original.count(old) == 1, 'upstream patch anchor')
        target.write_text(original.replace(old, new))
        patches.append({'path': relative, 'before': originals[relative],
                        'after': sha(target), 'old': old, 'new': new})
    guards = [
        ('pthread_mutex_lock', 'int __pthread_mutex_lock(pthread_mutex_t *m)', 'm->_m_type'),
        ('pthread_mutex_trylock', 'int __pthread_mutex_trylock(pthread_mutex_t *m)', 'm->_m_type'),
        ('pthread_mutex_timedlock', 'int __pthread_mutex_timedlock(pthread_mutex_t *restrict m, const struct timespec *restrict at)', 'm->_m_type'),
        ('pthread_mutex_unlock', 'int __pthread_mutex_unlock(pthread_mutex_t *m)', 'm->_m_type'),
        ('pthread_cond_timedwait', 'int __pthread_cond_timedwait(pthread_cond_t *restrict c, pthread_mutex_t *restrict m, const struct timespec *restrict ts)', 'c->_c_shared || m->_m_type'),
        ('pthread_cond_signal', 'int pthread_cond_signal(pthread_cond_t *c)', 'c->_c_shared'),
        ('pthread_cond_broadcast', 'int pthread_cond_broadcast(pthread_cond_t *c)', 'c->_c_shared'),
    ]
    for name, signature, condition in guards:
        relative = selection[name]
        target = headers / relative
        old = signature + '\n{\n'
        new = old + '\tif (' + condition + ') return ENOTSUP;\n'
        original = target.read_text()
        need(original.count(old) == 1, 'unsupported synchronization guard anchor')
        target.write_text(original.replace(old, new))
        patches.append({'path': relative, 'before': originals[relative],
                        'after': sha(target), 'old': old, 'new': new})
    shutil.copyfile(HERE / 'futex_syscall.h', headers / 'arch/x86_64/syscall_arch.h')
    env = proc.clean_env(output)
    commands = []

    def run(label, argv):
        result = proc.run([str(a) for a in argv], cwd=output, env=env,
                          work=output, label=label, timeout=120)
        commands.append({'label': label, 'argv': [str(a) for a in argv],
                         'record': result.record})
        (output / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        need(result.returncode == 0 and result.record['complete']
             and result.record['cleanup'] == 'complete', label)
        return result

    cc = [tools['clang']['path'], '--no-default-config',
          '--target=x86_64-linux-musl', '--sysroot=' + str(output / 'empty-root'),
          '-std=c17', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror',
          '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc',
          '-DAETHER_LONG_WAITS', '-Dhidden=__attribute__((__visibility__("hidden")))']
    for directory in ('src/include', 'src/internal', 'arch/x86_64', 'arch/generic'):
        cc += ['-isystem', headers / directory]
    cc += ['-isystem', sdk / 'stage/usr/include', '-I', HERE]
    objects = []
    for name, relative in list(selection.items()) + [('backend', None), ('real_time', None)]:
        flags = []
        if relative:
            flags += ['-Wno-unused-parameter', '-Wno-cast-function-type-mismatch']
            if name == 'cp':
                flags += ['-Wno-deprecated-non-prototype']
            if name in ('timedwait', 'pthread_cond_timedwait'):
                flags += ['-Wno-sign-compare']
            if name in ('pthread', 'join'):
                flags += ['-U_GNU_SOURCE']
            flags += ['-Dweak=__attribute__((__weak__))']
            flags += ['-Dweak_alias(old,new)=' if name == 'join' else
                      '-Dweak_alias(old,new)=extern __typeof(old) new __attribute__((__weak__,__alias__(#old)))']
        obj = output / (name + '.o')
        run(name, cc + flags + ['-c', headers / relative if relative else HERE / (name + '.c'),
                                '-o', obj])
        objects.append(obj)
    supplemental = output / 'libaether_runtime.a'
    run('archive', [tools['ar']['path'], 'rcs', supplemental, *objects])
    symbols = run('symbols', [tools['nm']['path'], '--defined-only', supplemental]).stdout
    (output / 'build.json').write_text(json.dumps({
        'profile': 'native-service-runtime-v0', 'status': 'built, execution required',
        'sources': {p.name: sha(p) for p in HERE.iterdir() if p.is_file()},
        'sdk_seal_sha256': sha(seal), 'sdk_members': sealed,
        'sdk_receipt_sha256': sha(receipt_path), 'base_libc_sha256': sha(sdk / 'stage/usr/lib/libc.a'),
        'upstream_sha256': sha(archive), 'tools': tools, 'patches': patches,
        'originals': originals, 'supplemental_sha256': sha(supplemental),
        'required_link': ['--whole-archive', 'libaether_runtime.a', '--no-whole-archive', 'libc.a'],
        'symbols_sha256': hashlib.sha256(symbols).hexdigest(),
    }, indent=2) + '\n')
    return output


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', action='version', version='aether-service-runtime 0')
    args = parser.parse_args()
    try:
        print(display(build(args.sdk, args.output)))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, display(error) + '\n')
