#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Separate borrowed Rust metadata/original-decoder READ-only qualification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT, verify
from fs_init_checks import build_reader
from fs_launch_intake import intake
from fs_session import ENGINE, machine_witness
from native_smoke import NativeStopError, run
from openzfs_namespace import native_media_snapshot, prepare_native_fixture
import service_runtime_smoke as runtime

VOLUME = ROOT/'user/storage/openzfs-volume'
BINDING = ROOT.parent/'Aether-userland/experiments/filesystem-service/metadata.rs'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def selected_owner(text):
    anchor = '    require(file.identity() == (2, 47))?;'
    if text.count(anchor) != 1:
        raise ValueError('metadata original owner context changed')
    text = re.sub(r'#\[path = "([^"]+)"\]',
                  lambda m: '#[path = '+json.dumps(str((VOLUME/m[1]).resolve()))+']', text)
    text += '\n#[path = '+json.dumps(str(BINDING))+']\nmod metadata;\n'
    text += '#[path = '+json.dumps(str(VOLUME/'metadata-check.rs'))+']\nmod metadata_check;\n'
    return text.replace(anchor, anchor+'''
    // SAFETY: backend owns this view and its SPA borrow. Fixed identities came
    // from its root/lookup above; no concurrent access or pointer retention.
    require(unsafe { metadata_check::check(backend.view, root.identity(), file.identity()) })?;''', 1)


def build(stage, command, tools):
    selected = stage.parent/'metadata-owner.rs'
    selected.write_text(selected_owner((VOLUME/'namespace-zpl.rs').read_text()))
    counts = {'provider': 0, 'owner': 0}

    def composition(argv, log, rejection=None):
        args = list(map(str, argv))
        if '-c' in args and args[args.index('-c')+1] == str(VOLUME/'zpl-read.c'):
            counts['provider'] += 1
            args[args.index('-c')+1] = str(VOLUME/'zpl-metadata.c')
        if str(VOLUME/'namespace-zpl.rs') in args:
            counts['owner'] += 1
            args[args.index(str(VOLUME/'namespace-zpl.rs'))] = str(selected)
            args += ['-Dunsafe_op_in_unsafe_fn']
        if any(value > 1 for value in counts.values()):
            raise ValueError('duplicate metadata composition')
        return command(args, log, rejection=rejection)

    result = build_reader(stage, composition, tools)
    if counts != {'provider': 1, 'owner': 1}:
        raise ValueError('missing metadata provider/owner composition')
    return dict(reader=result, selections=counts, binding_sha256=sha(BINDING),
                owner_sha256=sha(selected), provider_sha256=sha(VOLUME/'zpl-metadata.c'))


def qualify(execute=False):
    output = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-metadata-', dir=ROOT/'zig-out'))
    record = dict(format='aether-fs-metadata-qualification-v1', status='preparing',
                  start_utc=datetime.now(timezone.utc).isoformat(), output=str(output),
                  commands=[], inputs={}, artifacts={}, native_attempted=False,
                  limits=dict(host_seconds=30, kernel_ticks=3000, engine_pages=8192,
                              controller_bytes=4096, generations=3),
                  scope='Owner-only Rust metadata on original disk; no metadata RPC, mutation, POSIX policy, full service or Zsh/ISO acceptance')
    stopped = True

    def save():
        (output/'results.json').write_text(json.dumps(record, indent=2)+'\n')

    def command(argv, log, rejection=None):
        args = list(map(str, argv))
        try:
            with Path(log).open('w') as stream:
                result = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
        except subprocess.TimeoutExpired:
            # subprocess.run kills and joins its child before raising. Keep the
            # incomplete command as failed evidence; never retry it here.
            text = Path(log).read_text(errors='replace')
            record['commands'].append(dict(argv=args, timeout_seconds=180,
                status='timeout', log_sha256=sha(log), tail=text[-1500:]))
            save()
            raise
        text = Path(log).read_text(errors='replace')
        record['commands'].append(dict(argv=args, exit=result.returncode,
            expected_rejection=rejection, log_sha256=sha(log), tail=text[-1500:]))
        save()
        failed = (result.returncode == 0 or rejection not in text) if rejection else result.returncode != 0
        if failed:
            raise RuntimeError('metadata build/check failed: '+str(log))
        return text

    def freeze():
        intake(ENGINE)
        if sha(current/'current-inputs.json') != record['dependency']['sha256']:
            raise ValueError('metadata dependency manifest changed')
        for name, digest in manifest['files'].items():
            if sha(current/name) != digest:
                raise ValueError('metadata dependency drift: '+name)
        for name, digest in record['inputs'].items():
            if sha(name) != digest:
                raise ValueError('metadata frozen input drift: '+name)
        for name, digest in record['artifacts'].items():
            if sha(output/name) != digest:
                raise ValueError('metadata artifact drift: '+name)

    print('[RUNNING] Metadata qualification: '+str(output), file=sys.stderr, flush=True)
    try:
        verify()
        record['engine_intake'] = intake(ENGINE)
        current = ROOT/'.deps/native-current'
        manifest = json.loads((current/'current-inputs.json').read_text())
        record['dependency'] = dict(sha256=sha(current/'current-inputs.json'), members=len(manifest['files']))
        tools = json.loads((current/'sdk/tools.lock.json').read_text())['tools']
        record['tools'] = tools
        initial = [ROOT/'build.zig', ROOT/'boot/dependencies.json', BINDING]
        initial += [p for directory in ('kernel', 'user', 'scripts') for p in (ROOT/directory).rglob('*')
                    if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store']
        initial += [Path(t['path']).resolve() for t in tools.values()]
        initial += [Path(shutil.which(t)).resolve() for t in ('zig', 'qemu-system-x86_64', 'xorriso')]
        compiler = Path(subprocess.check_output(['rustup','which','--toolchain','1.98.0','rustc'], text=True).strip())
        libs = Path(subprocess.check_output([compiler,'--print','target-libdir','--target=x86_64-unknown-none'], text=True).strip())
        initial += [compiler, *libs.glob('*.rlib')]
        record['inputs'] = {str(p): sha(p) for p in initial}
        reference = ROOT/'docs/evidence/openzfs-zpl-namespace-host-2026-10-18.json'
        record['reference'] = dict(path=str(reference), sha256=sha(reference),
            scope='Original zdb namespace seconds/labels/flags; not nanos or new getter execution')
        record['inputs'][str(reference)] = sha(reference)
        for name in ('clang','lld','nm'):
            if sha(tools[name]['path']) != tools[name]['sha256']:
                raise ValueError('metadata tool pin: '+name)
        freeze()
        record['composition'] = build(output/'reader', command, tools)
        record['fixture'] = prepare_native_fixture(output)
        disk = output/'native-namespace.raw'
        before = native_media_snapshot(disk)
        record['media_before'] = before
        artifacts = [p for p in output.rglob('*') if p.is_file() and p.name != 'results.json']
        record['artifacts'] = {str(p.relative_to(output)): sha(p) for p in artifacts}
        freeze()
        record['status'] = 'prepared'; save()
        if execute:
            record['native_attempted'] = True; save()
            run(output/'reader/aether.iso', marker=b'AETHER NATIVE BLOCK PASS', entropy=True,
                rtc_base='2026-10-06T12:34:00', block_disk=disk,
                block_large=True, block_namespace=True, _pair_stop=True)
            record['vm_run_returned'] = True
            record['qemu'] = json.loads((output/'reader/native-qemu-command.json').read_text())
            record['media_after'] = native_media_snapshot(disk)
            if record['media_after'] != before:
                raise ValueError('metadata reader changed guarded media')
            serial = (output/'reader/native-serial.log').read_text()
            record['trace'] = {**runtime.check_engine_trace(serial, 'AETHER NATIVE BLOCK PASS'),
                              **runtime.check_pool_cleanup_trace(serial),
                              **runtime.check_namespace_trace(serial)}
            freeze()
            record.update(status='pass', metadata_nodes=2, stale_generation_denied=True,
                          whole_file_sha256='cc9bfddedd664b9a5334581af786516d149c3fbd2c7e65735985acf17bce5935',
                          timestamp_scope='zdb-reference seconds/labels/flags; native nanos range only, exact ABI tested on host')
        return output
    except BaseException as error:
        stopped = not isinstance(error, NativeStopError)
        record.update(status='failed', error=str(error), vm_stop_confirmed=stopped,
                      triage_required=record['native_attempted'])
        raise
    finally:
        serial = output/'reader/native-serial.log'
        if serial.is_file():
            text = serial.read_text(errors='replace')
            record['serial'] = dict(sha256=sha(serial), tail=text[-6000:], machine_witness=machine_witness(text))
        if stopped:
            count = sum(p.is_file() for p in output.rglob('*'))
            for path in output.iterdir():
                if path.is_dir(): shutil.rmtree(path)
                elif path.name != 'results.json': path.unlink()
            record['cleanup'] = dict(stopped=True, removed_generated_members=max(0,count-1), remaining='results.json only')
        else:
            record['cleanup'] = dict(stopped=False, retained=str(output))
        record['end_utc'] = datetime.now(timezone.utc).isoformat(); save()
        print(('[PASS] ' if record['status'] in ('pass','prepared') else '[FAIL] ')+str(output/'results.json'), file=sys.stderr)


if __name__ == '__main__':
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            print('[FAIL] '+runtime.display(message), file=sys.stderr)
            raise SystemExit(64)
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='aether-fs-metadata 1')
    parser.add_argument('--run', action='store_true', help='qualify one fresh READ-only guest; no retries')
    args = parser.parse_args()
    try:
        qualify(args.run)
    except Exception as error:
        print('[FAIL] '+runtime.display(error), file=sys.stderr)
        raise SystemExit(1)
