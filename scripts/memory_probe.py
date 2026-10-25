# SPDX-License-Identifier: BSD-2-Clause
"""Build the kernel conformance probe against an explicitly supplied strict musl build."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from deps import ROOT
from regression import Parser


def build(libc_build, tools_lock, output, fault, large=False, large_image=False, threads=False, waits=False, stacks=False, storage=False, libc_tls=False, indefinite=False, libc_wait=False, libc_lock=False, pthread_preflight=False, signal_mask=False, pthread_lifecycle=False, pair=False, pthread_keys=False, long_waits=False):
    libc_build, output = Path(libc_build).resolve(), Path(output).resolve()
    receipt = json.loads((libc_build / 'evidence.json').read_text())
    tools = json.loads(Path(tools_lock).read_text())['tools']
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(libc_build / 'stage/usr/lib/libc.a') != receipt['libc_archive_sha256']:
        raise RuntimeError('libc archive differs from its receipt')
    for name in ('clang', 'lld'):
        if sha(Path(tools[name]['path']).resolve()) != tools[name]['sha256']:
            raise RuntimeError('tool pin mismatch: ' + name)
    if not receipt.get('libc_patches'):
        raise RuntimeError('strict metadata-protection libc receipt required')
    output.mkdir(parents=True, exist_ok=False)
    if pthread_keys and not pthread_lifecycle:
        raise RuntimeError("pthread keys require the actual lifecycle profile")
    real_time = pthread_lifecycle and fault == "LIFE_REAL_TIME"
    if long_waits and not real_time:
        raise RuntimeError('long waits require the private real-time lifecycle profile')
    taskq = pthread_lifecycle and bool(fault) and fault.startswith("TASKQ_")
    private = []
    lifecycle_sources = {
        'musl_rw_rdlock': 'src/thread/pthread_rwlock_rdlock.c',
        'musl_rw_wrlock': 'src/thread/pthread_rwlock_wrlock.c',
        'musl_rw_tryrdlock': 'src/thread/pthread_rwlock_tryrdlock.c',
        'musl_rw_trywrlock': 'src/thread/pthread_rwlock_trywrlock.c',
        'musl_rw_timedrdlock': 'src/thread/pthread_rwlock_timedrdlock.c',
        'musl_rw_timedwrlock': 'src/thread/pthread_rwlock_timedwrlock.c',
        'musl_rw_unlock': 'src/thread/pthread_rwlock_unlock.c',
        'musl_cond_wait': 'src/thread/pthread_cond_wait.c',
        'musl_cond_timedwait': 'src/thread/pthread_cond_timedwait.c',
        'musl_cond_signal': 'src/thread/pthread_cond_signal.c',
        'musl_cond_broadcast': 'src/thread/pthread_cond_broadcast.c',
        'musl_mutex_lock': 'src/thread/pthread_mutex_lock.c',
        'musl_mutex_trylock': 'src/thread/pthread_mutex_trylock.c',
        'musl_mutex_timedlock': 'src/thread/pthread_mutex_timedlock.c',
        'musl_mutex_unlock': 'src/thread/pthread_mutex_unlock.c',
        'musl_join': 'src/thread/pthread_join.c',
        'musl_timedwait': 'src/thread/__timedwait.c',
        'musl_cp': 'src/thread/__syscall_cp.c',
        'musl_vm': 'src/thread/vmlock.c',
        'musl_block': 'src/signal/block.c',
        'musl_mmap': 'src/mman/mmap.c',
        'musl_mprotect': 'src/mman/mprotect.c',
        'musl_munmap': 'src/mman/munmap.c',
        'musl_wait': 'src/thread/__wait.c',
        'musl_lock': 'src/thread/__lock.c',
    }
    if real_time:
        lifecycle_sources.update({'musl_sleep': 'src/time/clock_nanosleep.c',
                                  'musl_nanosleep': 'src/time/nanosleep.c'})
    if taskq or pthread_keys or pthread_lifecycle and fault in ('LIFE_PAIR_KEYS', 'LIFE_KEYS_BYPASS', 'LIFE_PAIR_DETACHED', 'LIFE_REAP_EARLY'):
        lifecycle_sources.update({
            'musl_key_create': 'src/thread/pthread_key_create.c',
            'musl_key_set': 'src/thread/pthread_setspecific.c',
            'musl_key_get': 'src/thread/pthread_getspecific.c',
        })
    if pthread_lifecycle:
        pthread_preflight = libc_tls = True
    if libc_tls:
        archive_path = libc_build / 'musl-1.2.6.tar.gz'
        if not archive_path.is_file():
            archive_path = libc_build.parent / 'musl-audit/musl-1.2.6.tar.gz'
        if sha(archive_path) != receipt['source_sha256']:
            raise RuntimeError('musl private-header source pin mismatch')
        header_root = output / 'musl-headers'
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                relative = member.name.removeprefix('musl-1.2.6/')
                if member.isfile() and (relative in ('COPYRIGHT', 'src/include/features.h') or pthread_lifecycle and relative in lifecycle_sources.values() or libc_wait and relative == 'src/thread/__wait.c' or libc_lock and relative == 'src/thread/__lock.c' or pthread_preflight and relative == 'src/thread/pthread_create.c' or
                        relative.endswith('.h') and any(relative.startswith(p) for p in
                        (('src/internal/', 'arch/x86_64/', 'arch/generic/', 'src/include/', 'include/') if pthread_preflight else ('src/internal/', 'arch/x86_64/', 'arch/generic/')))):
                    target = header_root / relative
                    if '..' in Path(relative).parts or Path(relative).is_absolute():
                        raise RuntimeError('unsafe musl header path')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
        private = [str(header_root / p) for p in (('src/include', 'src/internal', 'arch/x86_64', 'arch/generic') if pthread_preflight else ('src/internal', 'arch/x86_64', 'arch/generic'))]
        (output / 'private-headers.json').write_text(json.dumps({str(p.relative_to(header_root)): sha(p)
            for p in header_root.rglob('*') if p.is_file()}, indent=2) + '\n')
    if libc_wait or pthread_preflight:
        (output / 'private-headers.json').rename(output / 'private-headers.original.json')
        (header_root / 'arch/x86_64/syscall_arch.h').write_bytes((ROOT / 'user/native-memory/futex_syscall.h').read_bytes())
        (output / 'private-headers.json').write_text(json.dumps({str(p.relative_to(header_root)): sha(p)
            for p in header_root.rglob('*') if p.is_file()}, indent=2) + '\n')
    if real_time:
        target = header_root / 'src/thread/__timedwait.c'
        original = target.read_text()
        old = '\tif (at) {\n'
        new = ('\tif (at) {\n'
               '\t\textern int aether_libc_timedwait(volatile int *, int, clockid_t, const struct timespec *, int);\n'
               '\t\treturn aether_libc_timedwait(addr, val, clk, at, !!priv);\n\t}\n' + old)
        if original.count(old) != 1:
            raise RuntimeError('musl absolute timedwait patch context mismatch')
        target.write_text(original.replace(old, new))
        (output / 'timedwait-patch.json').write_text(json.dumps({
            'before_sha256': hashlib.sha256(original.encode()).hexdigest(),
            'after_sha256': sha(target), 'old': old, 'new': new}, indent=2) + '\n')
    if pthread_preflight:
        target = header_root / 'src/thread/pthread_create.c'
        original = target.read_text()
        old = '\tself = __pthread_self();\n\tif (!libc.threaded)'
        new = '\tself = __pthread_self();\n#ifndef PTHREAD_SKIP_PREFLIGHT\n\tunsigned long native_mask = 0;\n\tint native_error = __syscall(SYS_rt_sigprocmask, SIG_SETMASK, 0, &native_mask, _NSIG/8);\n\tif (native_error < 0) return -native_error;\n#endif\n\tif (!libc.threaded)'
        if pthread_lifecycle:
            new = new.replace('\tunsigned long native_mask = 0;', '\textern int aether_pthread_admit(const void *);\n\tint admission = aether_pthread_admit(attrp);\n\tif (admission) return admission;\n\tunsigned long native_mask = 0;')
        if original.count(old) != 1:
            raise RuntimeError('pthread preflight patch context mismatch')
        (output / 'pthread_create.original.c').write_text(original)
        target.write_text(original.replace(old, new))
        (output / 'pthread-patch.json').write_text(json.dumps({'old':old,'new':new,
            'before_sha256':sha(output / 'pthread_create.original.c'),'after_sha256':sha(target)},indent=2)+'\n')
        (output / 'private-headers.json').write_text(json.dumps({str(p.relative_to(header_root)): sha(p)
            for p in header_root.rglob('*') if p.is_file()}, indent=2) + '\n')
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR') if k in os.environ}
    clang, lld = tools['clang']['path'], tools['lld']['path']
    lib = libc_build / 'stage/usr/lib'
    source = ROOT / 'user/native-memory'
    commands = []
    def run(command):
        commands.append(command)
        try:
            with (output / 'producer.log').open('ab') as log:
                subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=120)
        finally:
            (output / 'build-attempt.json').write_text(json.dumps({
                'commands': commands, 'fault': fault,
                'source_sha256': receipt['source_sha256']}, indent=2) + '\n')
    cc = [clang, '--no-default-config', '--target=x86_64-linux-musl',
          '--sysroot=' + str(libc_build / 'empty-root')]
    taskq_objects = []
    if taskq:
        taskq_root = ROOT / 'user/native-taskq'
        archive = ROOT / '.deps/sources/openzfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1.tar.gz'
        if sha(archive) != 'bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8':
            raise RuntimeError('taskq archive pin mismatch')
        with tarfile.open(archive) as t:
            original = t.extractfile('zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzpool/taskq.c').read()
        (output / 'taskq.original.c').write_bytes(original)
        (output / 'taskq.c').write_bytes(original + b'\n' + (taskq_root / 'tsd.inc').read_bytes())
        for name, path in [('taskq', output / 'taskq.c'), ('platform', taskq_root / 'platform.c')]:
            obj = output / (name + '.o')
            run(cc + ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc', '-isystem', str(libc_build / 'stage/usr/include'), '-I' + str(taskq_root / 'include'), '-I' + str(taskq_root), '-c', str(path), '-o', str(obj)])
            taskq_objects.append(str(obj))
        (output / 'taskq-inputs.json').write_text(json.dumps({str(p.relative_to(ROOT)): sha(p) for p in taskq_root.rglob('*') if p.is_file()}, indent=2) + '\n')
    for name in (('probe', 'musl_pthread', *lifecycle_sources, *(['real_time'] if real_time else [])) if pthread_lifecycle else ('probe', 'musl_pthread') if pthread_preflight else ('probe', 'adapter', 'libc_thread', 'musl_wait', 'musl_lock') if libc_lock else ('probe', 'adapter', 'libc_thread', 'musl_wait') if libc_wait else ('probe', 'adapter', 'libc_thread') if libc_tls else ('probe', 'adapter')):
        run(cc + ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror',
            '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc'] +
            (['-DAETHER_LONG_WAITS'] if long_waits else []) +
            ([item for directory in private for item in ('-isystem', directory)] if pthread_preflight else []) +
            ['-isystem', str(libc_build / 'stage/usr/include')] +
            (['-U_GNU_SOURCE'] if name in ('musl_pthread', 'musl_join') else []) +
            (['-Wno-unused-parameter', '-Wno-cast-function-type-mismatch'] if name.startswith('musl_') and pthread_lifecycle or name == 'musl_pthread' else []) +
            (['-Wno-deprecated-non-prototype'] if pthread_lifecycle and name == 'musl_cp' else []) +
            (['-Wno-sign-compare'] if pthread_lifecycle and name in ('musl_timedwait', 'musl_cond_timedwait') else []) +
            (['-Dweak_alias(old,new)=extern __typeof(old) new __attribute__((__weak__,__alias__(#old)))', '-Dweak=__attribute__((__weak__))'] if pthread_preflight else []) +
            (['-DLIFE_TASKQ', '-I' + str(taskq_root), '-I' + str(taskq_root / 'include')] if taskq and name == 'probe' else []) +
            (['-DSIGNAL_MASK'] if signal_mask else []) +
            (['-DLIBC_LOCK'] if libc_lock else []) +
            (['-DLIBC_WAIT'] if libc_wait else []) +
            (['-DINDEFINITE_WAIT'] if indefinite else []) +
            (['-DLIBC_TLS', '-Dhidden=__attribute__((__visibility__("hidden")))'] if libc_tls else []) +
            [item for directory in private for item in ('-isystem', directory)] +
            (['-D' + fault] if fault and name in ('probe', 'libc_thread', 'musl_pthread') else []) +
            (['-DLARGE_MEMORY'] if large and name == 'probe' else []) +
            ['-c', str(header_root / lifecycle_sources[name] if pthread_lifecycle and name in lifecycle_sources else source / 'pthread_lifecycle.c' if pthread_lifecycle and name == 'probe' else header_root / 'src/thread/pthread_create.c' if name == 'musl_pthread' else source / 'pthread_preflight.c' if name == 'probe' and pthread_preflight else header_root / 'src/thread/__lock.c' if name == 'musl_lock' else header_root / 'src/thread/__wait.c' if name == 'musl_wait' else source / ('pair.c' if name == 'probe' and pair else 'storage.c' if name == 'probe' and storage else 'stacks.c' if name == 'probe' and stacks else 'waits.c' if name == 'probe' and waits else 'threads.c' if name == 'probe' and threads else 'large-image.c' if name == 'probe' and large_image else name + '.c')), '-o', str(output / (name + '.o'))])
    run(cc + ['-fuse-ld=' + lld, '-nostdlib', '-static', '-Wl,-z,noexecstack',
        '-Wl,--no-undefined', '-Wl,-Map,' + str(output / 'probe.map'),
        str(lib / 'crt1.o'), str(lib / 'crti.o'), str(output / 'probe.o'),
        *([str(output / 'adapter.o')] if not pthread_preflight else []),
        *([str(output / 'libc_thread.o')] if libc_tls and not pthread_preflight else []),
        *([str(output / 'musl_wait.o')] if libc_wait else []),
        *([str(output / 'musl_lock.o')] if libc_lock else []),
        *([str(output / 'musl_pthread.o')] if pthread_preflight else []),
        *([str(output / (name + '.o')) for name in lifecycle_sources] if pthread_lifecycle else []),
        *([str(output / 'real_time.o')] if real_time else []),
        *taskq_objects,
        str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(output / 'probe.elf')])
    (output / 'native-c.bin').write_bytes(b'AENATC01' + os.urandom(32) + (output / 'probe.elf').read_bytes())
    (output / 'evidence.json').write_text(json.dumps({'scope': 'kernel conformance adapter; not production userland adoption',
        'commands': commands, 'libc_build': str(libc_build), 'libc_sha256': receipt['libc_archive_sha256'],
        'libc_receipt_sha256': sha(libc_build / 'evidence.json'),
        'sources': {p.name: sha(p) for p in source.iterdir() if p.is_file()},
        'envelope_sha256': sha(output / 'native-c.bin'), 'elf_sha256': sha(output / 'probe.elf'),
        'fault': fault, 'large': large, 'large_image': large_image, 'threads': threads, 'waits': waits, 'stacks': stacks, 'storage': storage, 'libc_tls': libc_tls, 'indefinite': indefinite, 'libc_wait': libc_wait, 'libc_lock': libc_lock, 'pthread_preflight': pthread_preflight, 'signal_mask': signal_mask, 'pthread_lifecycle': pthread_lifecycle, 'pair': pair, 'pthread_keys': pthread_keys}, indent=2) + '\n')
    print('[PASS] Memory probe built:', output)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--fault', choices=['FAULT_READ', 'FAULT_WRITE', 'FAULT_UNMAP', 'METADATA_DENIAL', 'STOP_LIVE'])
    parser.add_argument('--version', action='version', version='aether-memory-probe 1')
    args = parser.parse_args()
    try:
        build(args.libc_build, args.tools_lock, args.output, args.fault)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
