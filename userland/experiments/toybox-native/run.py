#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Replay captured cat profiles with rebuilt objects and owned processes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--profile', choices=('cat', 'errors', 'usage', 'finalize', 'close'), default='cat')
    args = parser.parse_args()
    snapshot = args.snapshot.resolve()
    intake = json.loads((snapshot / 'intake.json').read_text())
    extra = {}
    if args.profile != 'cat':
        extra = json.loads((snapshot / 'error-usage-inputs.json').read_text())
    pins = dict(intake['pins'], **extra)
    for name, digest in pins.items():
        if sha(snapshot / name) != digest:
            raise RuntimeError('snapshot drift: ' + name)
    kernel = snapshot / 'producer'
    host = json.loads((ROOT / 'experiments/command-runner/host-tools.lock.json').read_text())
    for tool in host.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise RuntimeError('host tool drift')
    tool_bin = snapshot / 'tools'
    tool_bin.mkdir(exist_ok=True)
    for name in ('zig', 'qemu-system-x86_64', 'xorriso'):
        path = tool_bin / name
        if not path.exists():
            path.symlink_to(host[name]['path'])
    path = tool_bin / 'python3'
    if not path.exists():
        path.symlink_to(sys.executable)
    wrapper = tool_bin / 'rustc'
    wrapper.write_text('#!' + sys.executable + '\nimport os,sys\n'
        + 'os.environ["DYLD_LIBRARY_PATH"]=' + repr(str(Path(host['rustc']['path']).parents[1] / 'lib')) + '\n'
        + 'compiler=' + repr(host['rustc']['path']) + '\n'
        + 'os.execv(compiler,[compiler]+[x for x in sys.argv[1:] if x!="+1.98.0"])\n')
    wrapper.chmod(0o755)
    original = kernel / ('docs/evidence/toybox-native-' + args.profile + '-2026-09-07/run-native.py')
    source = original.read_text()
    before = "rewrite=lambda a:[v.replace(old['output'],str(build)) for v in a]"
    after = "rewrite=lambda a:[v.replace('/Users/cam/DEV/Aether',str(ROOT)).replace(old['output'].replace('/Users/cam/DEV/Aether',str(ROOT)),str(build)) for v in a]"
    if source.count(before) != 1:
        raise RuntimeError('recipe path anchor')
    source = source.replace(before, after)
    start = source.index('def command(label, argv):')
    end = source.index('\ntry:', start)
    command = '''def command(label, argv):
    argv = list(argv)
    if argv[0] in host:
        argv[0] = host[argv[0]]['path']
    selected = dict(environment)
    if argv[0] == host['rustc']['path']:
        argv = [arg for arg in argv if arg != '+1.98.0']
        selected['DYLD_LIBRARY_PATH'] = str(Path(argv[0]).parents[1] / 'lib')
    result = owned_run(argv,cwd=ROOT,env=selected,work=out,label=label,
                       timeout=180,file_limit=512*1024**2)
    report['commands'].append(dict(label=label, **result.record))
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\\n')
    if not result.record['complete'] or result.returncode:
        raise RuntimeError(label+' failed')
'''
    source = source[:start] + command + source[end:]
    if args.profile in ('errors', 'finalize', 'close'):
        old_rust = "rust=Path(subprocess.check_output(['rustup','which','--toolchain','1.98.0','rustc'],text=True).strip())"
        if source.count(old_rust) != 1:
            raise RuntimeError('Rust selection anchor')
        source = source.replace(old_rust, "rust=Path(host['rustc']['path'])")
    anchor = "    command('adapter-scope',adapter_cmd)"
    rebuild = '''
    for entry in old['commands']:
        if '-c' in entry['argv'] and entry['label'] not in ('main','adapter'):
            command('rebuild-'+entry['label'],rewrite(entry['argv']))
'''
    if source.count(anchor) != 1:
        raise RuntimeError('recipe rebuild anchor')
    if args.profile != 'close':
        source = source.replace(anchor, anchor + rebuild)
    source = source.replace('from native_smoke import run as boot', '''def boot(image, expected_panic=None, panic_context=(), marker=b'AETHER NATIVE CONNECTIONS PASS'):
    payload=json.dumps(dict(panic=expected_panic.decode() if expected_panic else None,
                           context=[x.decode() for x in panic_context],marker=marker.decode()))
    program=('import sys,json; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
             'from native_smoke import run; p=json.loads(sys.argv[3]); '
             'run(Path(sys.argv[2]),expected_panic=p["panic"].encode() if p["panic"] else None, '
             'panic_context=tuple(x.encode() for x in p["context"]),marker=p["marker"].encode())')
    command(image.parent.name+'-boot',[sys.executable,'-B','-c',program,str(ROOT/'scripts'),str(image),payload])
''')
    sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
    from process import clean_env, run
    environment = clean_env(snapshot)
    environment['PATH'] = str(tool_bin) + ':/usr/bin:/bin'
    execution = Path(tempfile.mkdtemp(prefix=args.profile+'-execution-', dir=snapshot))
    candidate = execution / 'adapted-recipe.py'
    candidate.write_text(source)
    record = dict(intake_sha256=sha(snapshot/'intake.json'),driver_sha256=sha(Path(__file__)),
                  original_recipe_sha256=sha(original),adapted_recipe_sha256=sha(candidate),
                  host_tools=host,environment=environment,rust_wrapper_sha256=sha(wrapper),
                  process_sha256=sha(ROOT/'experiments/command-runner/process.py'),
                  profile=args.profile,extra_inputs=extra,
                  scope='Consumer source rebuild; errors also rebuild owner; backend payloads reused')
    (execution/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
    (execution/'run.py').write_text(Path(__file__).read_text())
    # __file__ retains the captured layout so the original recipe resolves private inputs.
    exec(compile(source,str(candidate),'exec'),dict(__file__=str(original),host=host,
         environment=environment,owned_run=run))
    for name, digest in pins.items():
        if sha(snapshot/name) != digest:
            raise RuntimeError('input changed during run: '+name)


if __name__ == '__main__':
    main()
