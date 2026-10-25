#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independently run the captured startup producer; never change its oracles."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import clean_env, run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    intake = ROOT / 'build/dash-startup-intake-lzvm3lp3'
    work = Path(tempfile.mkdtemp(prefix='dash-startup-native-', dir=ROOT / 'build'))
    report = dict(status='incomplete', work=str(work), commands=[])
    def save():
        (work / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
    print(work, file=sys.stderr, flush=True)
    save()
    try:
        retained = ROOT / 'docs/evidence/dash-startup-intake-2026-09-07'
        need(sha(intake / 'intake.json') == sha(retained / 'intake.json'), 'intake drift')
        record = json.loads((intake / 'intake.json').read_text())
        need(sha(intake / 'handoff.json') == record['producer_handoff_sha256'], 'handoff drift')
        handoff = json.loads((intake / 'handoff.json').read_text())
        for key in ('sources', 'source_manifest', 'sdk_receipt', 'tools'):
            v = handoff[key]
            need(sha(intake / v['path']) == v['sha256'], key + ' drift')
        need(sha(intake / 'sdk-inputs.tar.gz') == record['sdk_sha256'], 'SDK archive drift')
        pins = json.loads((intake / 'producer-source.json').read_text())
        kernel = intake / 'producer'
        for name, digest in pins.items():
            need(sha(kernel / name) == digest, 'source drift: ' + name)
        need(sha(ROOT / 'experiments/dash-native/startup.c') == handoff['consumer']['sha256'], 'consumer drift')
        with tarfile.open(intake / 'sdk-inputs.tar.gz') as archive:
            seen = set()
            for member in archive.getmembers():
                p = Path(member.name)
                need(not p.is_absolute() and '..' not in p.parts and p.parts[0] in ('native-c-5olokhku', 'musl-audit'), 'archive path')
                need(member.name not in seen, 'duplicate archive member')
                seen.add(member.name)
                need(member.isfile() or member.isdir() or
                     (member.issym() and member.name == 'native-c-5olokhku/obj/Makefile' and
                      member.linkname == '../musl-1.2.6/Makefile'), 'archive type/link')
            archive.extractall(work, filter='data')
        sdk = work / 'native-c-5olokhku'
        (sdk / 'empty-root').mkdir(exist_ok=True)
        sdk_files = {str(p.relative_to(sdk)): sha(p) for p in sdk.rglob('*') if p.is_file() and not p.is_symlink()}
        host = json.loads((ROOT / 'experiments/command-runner/host-tools.lock.json').read_text())
        native_tools = json.loads((intake / 'tools.lock.json').read_text())['tools']
        for t in [*host.values(), *native_tools.values()]:
            need(sha(Path(t['path'])) == t['sha256'], 'tool drift')
        private_tools = work / 'tools'; private_tools.mkdir()
        (private_tools / 'python3').symlink_to(sys.executable)
        report['python'] = dict(path=sys.executable, sha256=sha(Path(sys.executable)), version=sys.version)
        for name in ('zig', 'qemu-system-x86_64', 'xorriso'):
            (private_tools / name).symlink_to(host[name]['path'])
        old = ROOT / 'docs/evidence/toybox-close-regression-2026-09-07/results.json'
        old_receipt = json.loads(old.read_text())
        wrapper = ROOT / 'build/toybox-close-consumer-q91nkwbt/tools/rustc'
        need(sha(wrapper) == old_receipt['rust_wrapper_sha256'], 'wrapper drift')
        shutil.copy2(wrapper, private_tools / 'rustc')
        env = clean_env(work); env['PATH'] = str(private_tools) + ':/usr/bin:/bin'
        report.update(intake_sha256=sha(intake / 'intake.json'), driver_sha256=sha(Path(__file__)),
                      sources=pins, sdk_files=sdk_files, host_tools=host, native_tools=native_tools,
                      rust_wrapper_sha256=sha(wrapper), plan_sha256=sha(ROOT / 'experiments/dash-native/PLAN.md'))
        def command(label, argv, timeout):
            result = run(argv, cwd=kernel, env=env, work=work, label=label,
                         timeout=timeout, file_limit=512*1024**2)
            report['commands'].append(result.record); save()
            need(result.record['complete'] and result.returncode == 0, label + ' failed')
        command('host-tests', [host['zig']['path'], 'build', 'test', '--cache-dir',
                str(work / 'zig-cache'), '--global-cache-dir', str(work / 'zig-global')], 300)
        (kernel / 'zig-out').mkdir(exist_ok=True)
        before = set((kernel / 'zig-out').glob('command-runner-suite-*'))
        command('native', [sys.executable, '-B', 'scripts/launch_smoke.py', '--command-runner',
                '--libc-build', str(sdk), '--tools-lock', str(intake / 'tools.lock.json')], 1800)
        created = set((kernel / 'zig-out').glob('command-runner-suite-*')) - before
        need(len(created) == 1, 'ambiguous native output')
        result_path = created.pop() / 'results.json'
        result = json.loads(result_path.read_text())
        need(result['status'] == 'pass' and len(result['cases']) == 222, 'expected222 passing cases')
        for name, digest in pins.items():
            need(sha(kernel / name) == digest, 'source changed during run')
        report.update(status='pass', native_receipt=str(result_path),
                      native_receipt_sha256=sha(result_path), native_cases=222)
    except (OSError, ValueError, KeyError, RuntimeError, tarfile.TarError) as error:
        report['error'] = str(error)
    save(); print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
