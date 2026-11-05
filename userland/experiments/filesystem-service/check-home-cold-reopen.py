# SPDX-License-Identifier: BSD-2-Clause
"""Focused #150 engine bootstrap/result checks; no complete engine or guest.

Run from repository root with the retained filesystem-transport tool record:
python3 -B userland/experiments/filesystem-service/check-home-cold-reopen.py --inputs INPUTS_JSON
The default input location is userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json;
public source distributions omit that private prerequisite. An optional --evidence
PATH retains only the compact JSON result there. Help/version and versioned JSON
results use stdout; diagnostics use stderr. Output is ASCII without styling.
Use --ordering-only for the diagnosed final-zero ordering regression only.
Exits: 0 pass/help/version, 1 check failure, 2 missing prerequisite, 64 usage.
"""
import argparse
import hashlib
import json
import runpy
from pathlib import Path
import sys
import time

S = Path(__file__).resolve().parent
R = S.parents[2]
sys.path.insert(0, str(R / 'sys-init/scripts'))
from bounded_capture import OwnedTemporaryDirectory, run_capture_bytes


class PrerequisiteError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def format_help(self):
        purpose = self.description
        self.description = None
        try:
            return purpose + '\n\n' + super().format_help()
        finally:
            self.description = purpose

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[FAILED] ' + ascii(message)[1:-1] + '\n')


def check_ordering(run, work, tools, common, flags, sdk, report):
    rust = tools['rustc']['path']
    run('order-rust-results-build', [rust, *common, '--cfg', 'fs_home_cold_reopen', '--test',
        S / 'home-native-result.rs', '-o', work / 'order-results'])
    run('order-rust-results', [work / 'order-results', '--test-threads=1'])
    for name, cfg in (('cold', 'fs_home_cold_reopen'), ('writer', 'fs_home_terminfo_seven')):
        run('order-launch-' + name + '-build', [rust, *common, *flags, '--cfg', cfg, '--test',
            S / 'launch-home-owner.rs', '-o', work / ('order-launch-' + name)])
        case = ('tests::cold_reopen_requires_exact_zero_and_all_completion_obligations' if name == 'cold'
                else 'tests::terminfo_seven_requires_exact_count_and_complete_clean_result')
        run('order-launch-' + name, [work / ('order-launch-' + name), '--exact', case, '--test-threads=1'])
    source = (S / 'native-home.rs').read_text()
    start = source.index('    // Only the complete final zero-mutation report')
    end = source.index('    if clean {\n        0', start)
    block = source[start:end]
    report['producer_settlement_body_sha256'] = hashlib.sha256(block.encode()).hexdigest()
    producer = work / 'order-producer.rs'
    producer.write_text('#[path = ' + json.dumps(str(S / 'home-native-result.rs')) + '] pub mod result;\n'
        'use result::*;\nfn settle(output: &mut HomeResult, clean: bool) {\n' + block + '}\n'
        '#[path = ' + json.dumps(str(S / 'home-cold-producer-tests.rs')) + '] mod tests;\n')
    run('order-producer-build', [rust, *common, '--cfg', 'fs_home_cold_reopen', '--test',
        producer, '-o', work / 'order-producer'])
    run('order-producer', [work / 'order-producer', '--exact',
        'tests::producer_discharges_only_complete_healthy_zero_after_settlement', '--test-threads=1'])
    sys.path.insert(0, str(R / 'scripts'))
    from openzfs_fs_bulk import bulk_lifetime_record
    selected = bulk_lifetime_record((R / 'user/storage/openzfs-volume/pool-lifetime.inc').read_text())
    body = selected[selected.index('unsigned aether_pool_hooks_check_ordered(void)'):]
    report['actual_ordered_check_body_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    (work / 'cold-selected-ordered-body.inc').write_text(body)
    generator = runpy.run_path(str(S / 'home_native_source.py'))
    generated = []
    for filename in ('filesystem-engine.c', 'filesystem-import.c'):
        original = R / ('user/storage/service-runtime/' if filename == 'filesystem-engine.c'
                        else 'user/storage/openzfs-volume/') / filename
        text, _ = generator['render'](original)
        target = work / ('home-' + filename)
        target.write_text(text)
        generated.append(target)
        report.setdefault('generated_lifecycle', {})[filename] = hashlib.sha256(text.encode()).hexdigest()
    include = [S / 'home-native-host', S, work, R / 'user/storage/service-runtime',
               R / 'user/storage/openzfs-volume', R / 'user/storage/openzfs-elapsed',
               R / 'userland/experiments/native-service-runtime', R / 'userland/experiments/native-utc']
    for name, extra in (('cold', ['-DAETHER_FS_HOME_COLD_REOPEN']), ('writer', [])):
        run('order-c-predicate-' + name + '-build', [tools['clang']['path'], '-std=c17', '-Wall', '-Wextra', '-Werror',
            '-isysroot', sdk, *['-I' + str(p) for p in include], *extra,
            S / 'home-cold-result-tests.c', '-o', work / ('order-predicate-' + name)])
        run('order-c-predicate-' + name, [work / ('order-predicate-' + name)])
        binary = work / ('order-lifecycle-' + name)
        run('order-lifecycle-' + name + '-build', [tools['clang']['path'], '-std=c17', '-D_DEFAULT_SOURCE',
            '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
            '-DAETHER_FS_HOST_BLOCK_CLOSE=home_host_block_close',
            '-include', S / 'home-native-host/home-native-host.h', *['-I' + str(p) for p in include],
            *extra, *generated, S / 'home-cold-order-tests.c', '-o', binary])
        for case in ((0, 1, 9, 11, 18, 21, 26, 27, 28, 29) if name == 'cold' else (0, 1)):
            run('order-lifecycle-' + name + '-' + str(case), [binary, str(case)])


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='aether-home-cold-reopen-check 0.1')
    parser.add_argument('--inputs', type=Path,
                        default=R / 'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json',
                        help='retained filesystem-transport tool JSON (private prerequisite)')
    parser.add_argument('--ordering-only', action='store_true',
                        help='check only final-zero ordering and generated lifecycle consumers')
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    try:
        pins = json.loads(args.inputs.read_text())
        tools = pins['tools']
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise PrerequisiteError(
            'required filesystem-transport tool inputs unavailable or invalid: '
            + str(args.inputs) + '; use --inputs PATH to the retained input JSON') from error
    report = dict(schema='aether-home-cold-reopen-check-v1', rows=[], native_executed=False,
                  scope=('Actual final-zero predicates/producer settlement and generated importer/engine; host substitutions only.'
                         if args.ordering_only else
                         'Actual current bootstrap body, C/Rust result predicates and launcher; typed host storage only.'))
    deadline = time.monotonic() + 300
    started = time.monotonic()
    try:
        with OwnedTemporaryDirectory(prefix='home-cold-check-', dir=R / 'userland/build') as owner:
            work = Path(owner.name)
            def run(label, argv, expected=0):
                env = dict(PATH='/usr/bin:/bin', LC_ALL='C', TMPDIR=str(work))
                if str(argv[0]) in (tools['rustc']['path'], tools['rustfmt']['path']):
                    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
                remaining = deadline - time.monotonic()
                if remaining <= 10:
                    raise RuntimeError('aggregate deadline before ' + label)
                result = run_capture_bytes(list(map(str, argv)), cwd=R, env=env,
                    timeout=min(180, remaining - 10), deadline=deadline,
                    limit=4 * 1024**2, file_limit=16 * 1024**2, owner=owner,
                    record_path=str(work / (label + '.process.json')))
                report['rows'].append(dict(label=label, argv=list(map(str, argv)), expected_exit=expected, process=result.record,
                    stdout=result.stdout.decode(errors='replace')[-6000:], stderr=result.stderr.decode(errors='replace')[-6000:]))
                if not (result.returncode == expected and result.record['cleanup'] == 'complete'
                        and result.record['stdout_eof'] and result.record['stderr_eof']
                        and result.record['group_absent']):
                    raise RuntimeError(label)
                return result
            common = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
            profile = ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime', 'activation',
                       'names', 'directories', 'metadata', 'directory_contexts', 'home', 'home_wire',
                       'home_native', 'home_activation')
            flags = [item for name in profile for item in ('--cfg', 'fs_' + name)]
            rust = tools['rustc']['path']
            if not args.ordering_only:
                run('builder-selectors', ['/usr/bin/python3', '-B', S / 'home_engine_build_tests.py'])
                run('rust-results-build', [rust, *common, '--cfg', 'fs_home_cold_reopen', '--test',
                    S / 'home-native-result.rs', '-o', work / 'results'])
                run('rust-results', [work / 'results', '--test-threads=1'])
                sdk = run('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
                for name, extra in (('cold', ['-DAETHER_FS_HOME_COLD_REOPEN']), ('writer', [])):
                    run('c-' + name + '-build', [tools['clang']['path'], '-std=c17', '-Wall', '-Wextra', '-Werror',
                        '-isysroot', sdk, '-I' + str(S), '-I' + str(R / 'user/storage/service-runtime'),
                        *extra, S / 'home-cold-result-tests.c', '-o', work / ('c-' + name)])
                    run('c-' + name, [work / ('c-' + name)])
                for name, cfg in (('cold', 'fs_home_cold_reopen'), ('writer', 'fs_home_terminfo_seven')):
                    run('launch-' + name + '-build', [rust, *common, *flags, '--cfg', cfg, '--test',
                        S / 'launch-home-owner.rs', '-o', work / ('launch-' + name)])
                    run('launch-' + name, [work / ('launch-' + name), '--test-threads=1'])
                for mixed in ('fs_home_probe_three', 'fs_home_terminfo_six', 'fs_home_terminfo_seven', 'fs_af09_drain'):
                    refused = run('reject-' + mixed, [rust, *common, *flags, '--cfg', 'fs_home_cold_reopen',
                        '--cfg', mixed, '--crate-type=lib', '--emit=metadata', S / 'launch-home-owner.rs',
                        '-o', work / 'rejected.rmeta'], expected=1)
                    if b'fs_home_cold_reopen requires its closed' not in refused.stderr:
                        raise RuntimeError('wrong mixed-profile rejection: ' + mixed)
                run('metadata-build', [rust, *common, *flags, '--crate-type=lib', '--crate-name=filesystem_metadata',
                    S / 'metadata-lib.rs', '-o', work / 'libfilesystem_metadata.rlib'])
                run('policy-build', [rust, *common, *flags, '--crate-type=lib', '--crate-name=filesystem_policy',
                    '--extern', 'filesystem_metadata=' + str(work / 'libfilesystem_metadata.rlib'),
                    '-Ldependency=' + str(work), S / 'owner.rs', '-o', work / 'libfilesystem_policy.rlib'])
                source = (S / 'native-home.rs').read_text()
                begin = source.index('fn bootstrap<')
                end = source.index('/// Trusted synchronous importer', begin)
                bootstrap = source[begin:end]
                report['bootstrap_body_sha256'] = hashlib.sha256(bootstrap.encode()).hexdigest()
                wrapper = work / 'bootstrap.rs'
                wrapper.write_text('pub mod filesystem_bridge { pub use filesystem_policy as policy; }\n'
                    'use filesystem_policy::{Owner, Error, Handle, Kind, Rights, Session};\n'
                    '#[path = ' + json.dumps(str(S / 'home-native-result.rs')) + '] pub mod result;\n'
                    'use result::*;\n' + bootstrap + '\n#[path = '
                    + json.dumps(str(S / 'home-cold-bootstrap-tests.rs')) + '] mod tests;\n')
                run('bootstrap-build', [rust, *common, *flags, '--cfg', 'fs_home_cold_reopen',
                    '--extern', 'filesystem_policy=' + str(work / 'libfilesystem_policy.rlib'),
                    '-Ldependency=' + str(work), '--test', wrapper, '-o', work / 'bootstrap'])
                run('bootstrap', [work / 'bootstrap', '--test-threads=1'])
            else:
                sdk = run('order-host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
                check_ordering(run, work, tools, common, flags, sdk, report)
        report['status'] = 'pass'
    except BaseException as error:
        report['status'] = 'failed'
        report['failure'] = repr(error)
        raise
    finally:
        report['elapsed_seconds'] = time.monotonic() - started
        text = json.dumps(report, indent=2) + '\n'
        if args.evidence:
            args.evidence.write_text(text)
        else:
            print(text)


if __name__ == '__main__':
    try:
        main()
    except PrerequisiteError as error:
        sys.stderr.write('[BLOCKED] ' + ascii(str(error))[1:-1] + '\n')
        sys.exit(2)
    except Exception as error:
        sys.stderr.write('[FAILED] ' + ascii(str(error))[1:-1] + '\n')
        sys.exit(1)
