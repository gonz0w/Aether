# SPDX-License-Identifier: BSD-2-Clause
"""Check the finite native-home producer offline; no guest or complete engine fit."""
import json
import runpy
import shutil
from pathlib import Path
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
home = runpy.run_path(str(S / 'check-home-wire.py'))


def check_policy(record, work, proc, tools, deadline):
    env = proc.clean_env(work)
    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    flags = [*home['cfg'](True), '--cfg', 'fs_home_wire', '--cfg', 'fs_home_native']
    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        home['require'](remaining > 0, 'deadline before ' + label)
        result = proc.run(list(map(str, argv)), cwd=home['R'], env=env, work=work,
                          label=label, timeout=min(60, remaining))
        record['rows'].append({'label': label, 'expected_exit': expected,
            'process': result.record, 'stdout': result.stdout.decode(errors='replace')[-7000:],
            'stderr': result.stderr.decode(errors='replace')[-5000:]})
        home['require'](result.returncode == expected and result.record['complete']
                        and result.record['cleanup'] == 'complete', label)
        return result
    def deps(folder, names):
        return ['-Ldependency=' + str(folder), *[v for n in names for v in
            ('--extern', n + '=' + str(folder / ('lib' + n + '.rlib')))]]
    crates = [('filesystem_metadata','metadata-lib.rs',[]),
              ('filesystem_policy','owner.rs',['filesystem_metadata']),
              ('filesystem_service','service.rs',['filesystem_policy'])]
    for stage, extra in (('host',[]),('native',home['NATIVE'])):
        folder = work / ('policy-' + stage)
        folder.mkdir()
        for name, filename, imports in crates:
            common = [v for v in home['COMMON'] if name != 'filesystem_metadata' or v != '-Funsafe-code']
            run(stage + '-' + name,[tools['rustc']['path'],*common,*flags,*extra,*deps(folder,imports),
                '--crate-type=lib','--crate-name='+name,S/filename,'-o',folder/('lib'+name+'.rlib')])
    host = work / 'policy-host'
    imports = [name for name,_,_ in crates]
    run('policy-tests-build',[tools['rustc']['path'],*home['COMMON'],*flags,*deps(host,imports),
        '--test',S/'home-native-policy-tests.rs','-o',work/'policy-tests'])
    tested=run('policy-tests',[work/'policy-tests','--test-threads=1'])
    home['require'](b'5 passed; 0 failed' in tested.stdout,'five actual policy methods')
    record['policy_methods']=5

    for stage, extra in (('host', []), ('native', home['NATIVE'])):
        folder = work / ('policy-' + stage)
        for name, filename, imports_ in crates[1:]:
            run(stage + '-clippy-' + name, [tools['clippy-driver']['path'], *home['COMMON'],
                *flags, *extra, *deps(folder, imports_), '--crate-type=lib', '--crate-name='+name,
                S/filename, '-o', work/(stage+name+'-clippy.rlib')])
    run('policy-tests-clippy', [tools['clippy-driver']['path'], *home['COMMON'], *flags,
        *deps(host, imports), '--test', S/'home-native-policy-tests.rs', '-o', work/'policy-clippy'])
    run('policy-rustfmt', [tools['rustfmt']['path'], '--edition=2021', '--check',
        *[S/name for name in ('owner.rs','namespace-policy.rs','home-policy.rs','service.rs',
            'bulk-service.rs','names-service.rs','home-native-policy-tests.rs')]])
    controls = [
        ('provider-observation','namespace-policy.rs','*provider = Some(result);',
         'let _ = (&provider, result);','typed_provider_and_returned_outcomes_remain_distinct',
         'HOME_NATIVE_PROVIDER_RETENTION'),
        ('root-identity','home-policy.rs','home.node.identity() == self.root.identity()',
         'false','home_source_validation_uses_node_identity_and_original_checks','HOME_NATIVE_ROOT_IDENTITY'),
        ('mutation-cap','namespace-policy.rs','if self.writes == MUTATION_LIMIT {',
         'if self.writes == MUTATION_LIMIT && false {','bootstrap_and_later_calls_share_nine_attempts','HOME_NATIVE_MUTATION_CAP'),
        ('report-count','names-service.rs','let mutation_attempts = owner.mutation_attempts();',
         'let mutation_attempts = 0;','finite_loop_preserves_pre_loop_mutation_count_and_stops_before_receive_97',
         'HOME_NATIVE_REPORT_COUNT'),
    ]
    record['policy_controls'] = []
    for label, filename, before, after, case, marker in controls:
        folder = work / ('policy-control-' + label)
        folder.mkdir()
        # Copy only this real policy/service closure, never mutate live inputs.
        for source in S.glob('*.rs'):
            if not source.name.startswith(('native-home','launch-home','home-native-result')):
                shutil.copy2(source, folder/source.name)
        original=(S/filename).read_text()
        home['require'](original.count(before)==1,'unique policy control '+label)
        (folder/filename).write_text(original.replace(before,after,1))
        for name, filename_, imports_ in crates:
            common=[v for v in home['COMMON'] if name!='filesystem_metadata' or v!='-Funsafe-code']
            run(label+'-'+name,[tools['rustc']['path'],*common,*flags,*deps(folder,imports_),
                '--crate-type=lib','--crate-name='+name,folder/filename_,'-o',folder/('lib'+name+'.rlib')])
        run(label+'-control-build',[tools['rustc']['path'],*home['COMMON'],*flags,*deps(folder,imports),
            '--test',folder/'home-native-policy-tests.rs','-o',folder/'tests'])
        rejected=run(label+'-control-reject',[folder/'tests','--exact',case,'--nocapture'],expected=101)
        home['require'](b'1 failed' in rejected.stdout and case.encode() in rejected.stdout
                        and marker.encode() in rejected.stderr,'named semantic policy control '+label)
        record['policy_controls'].append(dict(label=label,file=filename,before=before,after=after,
            test=case,marker=marker,sha256=home['sha'](folder/filename)))


def check(record, work, proc, tools):
    deadline = time.monotonic() + 300
    pins = json.loads(home['PINS'].read_text())
    for name, tool in pins['tools'].items():
        home['verify'](tool['path'], tool['sha256'])
        tools[name] = tool
    for path, digest in pins['clang_resource_headers'].items():
        home['verify'](path, digest)
        record['sources'][path] = digest
    check_policy(record, work, proc, tools, deadline)
    for filename in ('home_native_c_checks.py', 'home_native_entry_checks.py'):
        module = runpy.run_path(str(S / filename))
        try:
            module['check'](record, work, proc, tools, deadline)
        except FileNotFoundError as error:
            raise home['PreconditionError'](
                'required native producer input unavailable: ' + str(error.filename)) from error
    record['limitations'] = (
        'Offline host substitutes and target objects only; no guest, actual OpenZFS execution, '
        'native authority/peak/settlement, complete engine fit or release acceptance.'
    )


if __name__ == '__main__':
    sys.exit(home['main'](check_function=check, program='aether-home-native-check',
        evidence=home['R']/'docs/evidence/filesystem-home-native-2026-10-24',
        description=__doc__,example='python3 -B experiments/filesystem-service/check-home-native.py',
        scope='finite native-home producer host/target and selected original C lifecycle checks; no guest or complete engine fit',
        extra_sources=(SOURCE, *sorted(S.glob('*.py')), *sorted(S.glob('*.c')),
            *sorted(S.glob('*.h')), *sorted((S/'home-native-host').rglob('*.h'))),
        limitations='No guest, actual OpenZFS execution or complete engine fit is tested.'))
