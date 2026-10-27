# SPDX-License-Identifier: BSD-2-Clause
"""Host-only mocked AF09 leaf composition; no compiler or target execution."""
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

S = Path(__file__).resolve().parent
CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
         'partial_ack', 'exit_deadline', 'pending_fragment')


def module(name):
    spec = importlib.util.spec_from_file_location(name, S / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def setUpModule():
    global deny_spawn
    deny_spawn = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('no real subprocess in mocked leaf tests'))
    deny_spawn.start()


def tearDownModule():
    deny_spawn.stop()


class Process:
    def __init__(self):
        self.calls = []
        self.fail = None
        self.mutate = None

    def clean_env(self, work):
        return {}

    def run(self, argv, **options):
        self.calls.append((options['label'], argv))
        if '-o' in argv:
            Path(argv[argv.index('-o') + 1]).write_bytes(b'synthetic object, never executed')
        for arg in argv:
            if arg.startswith('-Map='):
                Path(arg.split('=', 1)[1]).write_text('entry.o:(.text.aether_fs_home_run)')
        label = options['label']
        stdout = b''
        if label.endswith('-undefined'):
            stdout = b' U _DYNAMIC\n'
        elif label.endswith('-relocations'):
            stdout = b'There are no relocations in this file.'
        elif label.endswith('-elf'):
            stdout = b'ELF64 X86-64 TLS REL (Relocatable file)'
        elif label == 'home-engine-rust-service-symbols':
            stdout = b'0000 T aether_fs_home_run\n'
        elif label == 'home-engine-rust-launch-symbols':
            stdout = b'0000 T main\n0010 T aether_fs_home_launch_serve\n'
        if self.mutate:
            self.mutate()
        complete = label != self.fail
        return SimpleNamespace(returncode=0, stdout=stdout, stderr=b'',
            record={'complete': complete, 'cleanup': 'complete' if complete else 'unresolved'})


class ProbeBuildSelection(unittest.TestCase):
    def setUp(self):
        self.builder = module('home_probe_build')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / 'work'
        self.work.mkdir()
        self.deps = ((self.root / 'frame', 'frame-pin'), (self.root / 'session', 'session-pin'))
        bundle = self.deps[1][0] / 'bundle'
        bundle.mkdir(parents=True)
        include = self.root / 'build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'
        include.mkdir(parents=True)
        (include / 'one.h').write_text('/* synthetic header */')
        self.deps[0][0].mkdir()
        (self.deps[0][0] / 'dependency.json').write_text(json.dumps(
            {'native_header_pins': {str(include / 'one.h'): 'same'}}))
        dash = ['@bundle/producer/user/native-command/dash-inputs/obj/src/unit' + str(i) + '.o'
                for i in range(31)] + ['@bundle/producer/user/native-command/dash-main-inputs/main.o']
        common = ['@bundle/sdk/stage/usr/lib/crt1.o', '@bundle/sdk/stage/usr/lib/crti.o',
                  '@output/memory.o', '@bundle/sdk/stage/usr/lib/libc.a',
                  '@bundle/sdk/stage/usr/lib/crtn.o']
        fork = ['@output/public-fork/' + name + '.o' for name in
                ('fork', '_Fork', 'rebind', 'waitpid', 'wait3', 'wait4')]
        recipe = {'commands': [
            {'name': name, 'argv': ['/selected/clang', '-DREBIND_LIBC_REPAIR', '-o',
                                   '@output/public-fork/' + name.split('-')[0] + '.o']}
            for name in ('fork-compile', '_Fork-compile', 'rebind-compile', 'waitpid-compile',
                         'wait3-compile', 'wait4-compile', 'memory-compile')] + [
            {'name': 'parent-link', 'argv': [*common, *dash, *fork,
                '@output/parent-runtime.o', '@output/parent-application.o']},
            {'name': 'helper-link', 'argv': [*common, '@output/helper-runtime.o',
                '@output/helper-application.o', '@output/helper-body.o']}]}
        self.recipe_path = bundle / 'recipe.json'
        self.recipe_path.write_text(json.dumps(recipe))
        self.tools = {name: {'path': '/selected/' + name, 'sha256': 'same'}
                      for name in ('clang', 'lld', 'nm', 'readelf')}
        self.proc = Process()
        self.record = {}

    def build(self, case='none'):
        with mock.patch.object(self.builder, 'R', self.root), \
                mock.patch.object(self.builder, 'DEPENDENCIES', self.deps), \
                mock.patch.object(self.builder, 'sha', return_value='same'), \
                mock.patch.object(self.builder, 'verify', return_value={'synthetic': True}):
            return self.builder.build(self.work, self.proc, self.tools, time.monotonic() + 30,
                                      self.record, drain_case=case)

    def test_all_eight_cases_use_drain_parent_and_ordinary_allowed_helper(self):
        for case_id, case in enumerate(CASES, 1):
            with self.subTest(case=case):
                self.work = self.root / ('work-' + case)
                self.work.mkdir()
                self.proc = Process()
                result = self.build(case)
                calls = dict(self.proc.calls)
                parent = calls['home-complete-shell-link']
                helper = calls['home-complete-helper-link']
                self.assertEqual(result['drain_case'], case)
                self.assertEqual(result['drain_case_id'], case_id)
                self.assertEqual(result['profile']['selection'], 'fs_af09_drain')
                self.assertEqual(result['profile']['provider_attempts'], 2)
                self.assertIn(str(self.work / 'home-probe-native/fd-home-drain.o'), parent)
                self.assertIn(str(self.work / 'home-probe-native/fd-shell-entry.o'), parent)
                self.assertFalse(any('native-command/dash-' in a for a in parent))
                self.assertFalse(any(a.endswith('/fd-home-probe.o') for a in parent))
                self.assertFalse(any(a.endswith('/fd-home-drain.o') for a in helper))
                for name in ('fd-command-entry', 'fd-home-probe', 'fd-home-probe-adapter'):
                    self.assertTrue(any(a.endswith('/' + name + '.o') for a in helper))
                for name in ('crt1.o', 'crti.o', 'libc.a', 'crtn.o', 'fork.o', '_Fork.o',
                             'rebind.o', 'waitpid.o', 'wait3.o', 'wait4.o', 'memory.o'):
                    self.assertTrue(any(a.endswith('/' + name) for a in parent), name)
                macro = '-DAEFD_HOME_DRAIN_CASE=' + str(case_id)
                self.assertIn(macro, calls['home-target-fd-home-drain'])
                for label, argv in self.proc.calls:
                    if label != 'home-target-fd-home-drain':
                        self.assertFalse(any(a.startswith('-DAEFD_HOME_DRAIN_CASE=') for a in argv))
                selection = result['selection']
                self.assertEqual(selection, self.record['home_probe_selection'])
                self.assertEqual(len(selection['excluded_parent_objects']), 32)
                self.assertEqual(selection['case_flags'], [macro])
                self.assertIn(str(S / 'fd-home-drain.c'), result['sources'])
                self.assertEqual(selection['parent_objects'], [a for a in parent if a.endswith(('.o', '.a'))])
                self.assertEqual(selection['helper_objects'], [a for a in helper if a.endswith(('.o', '.a'))])
                self.assertEqual(self.record['home_probe_source_verification'], 'pass')

    def test_default_preserves_profile_dash_parent_and_old_helper(self):
        result = self.build()
        self.assertEqual(result['profile'], self.builder.PROFILE)
        self.assertEqual(set(result), {'shell', 'helper', 'sources', 'flags', 'dependencies',
                                      'artifacts', 'tools', 'profile'})
        self.assertNotIn('home_probe_selection', self.record)
        calls = dict(self.proc.calls)
        self.assertEqual(sum('native-command/dash-' in a for a in calls['home-complete-shell-link']), 32)
        self.assertNotIn('home-target-fd-home-drain', calls)
        self.assertNotIn(str(S / 'fd-home-drain.c'), result['sources'])

    def test_invalid_selection_has_no_work_or_process_effect(self):
        for case in (None, '', 'none ', 1, True, [], 'unknown'):
            proc = mock.Mock()
            work = self.root / 'uncreated'
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, 'AF09 drain case'):
                self.builder.build(work, proc, {}, 0, {}, drain_case=case)
            self.assertFalse(work.exists())
            proc.clean_env.assert_not_called()
            proc.run.assert_not_called()

    def test_inexact_dash_inventory_rejects_before_selected_link(self):
        recipe = json.loads(self.recipe_path.read_text())
        recipe['commands'][-2]['argv'].append('@bundle/producer/user/native-command/unknown/extra.o')
        self.recipe_path.write_text(json.dumps(recipe))
        with self.assertRaisesRegex(RuntimeError, 'exact retained Dash'):
            self.build('stream')
        self.assertNotIn('home-complete-shell-link', dict(self.proc.calls))

    def test_tool_identity_rejects_before_first_command(self):
        self.tools['clang']['sha256'] = 'wrong'
        with self.assertRaisesRegex(RuntimeError, 'tool pin: clang'):
            self.build('stream')
        self.assertEqual(self.proc.calls, [])

    def test_tool_change_during_commands_rejects_final_verification(self):
        def digest(path):
            return 'changed' if str(path) == '/selected/clang' and self.proc.calls else 'same'
        with mock.patch.object(self.builder, 'R', self.root), \
                mock.patch.object(self.builder, 'DEPENDENCIES', self.deps), \
                mock.patch.object(self.builder, 'sha', side_effect=digest), \
                mock.patch.object(self.builder, 'verify', return_value={'synthetic': True}):
            with self.assertRaisesRegex(RuntimeError, 'tools changed during build'):
                self.builder.build(self.work, self.proc, self.tools, time.monotonic() + 30,
                                   self.record, drain_case='stream')
        self.assertNotIn('home_probe_source_verification', self.record)

    def test_selected_source_change_rejects_final_verification(self):
        def digest(path):
            return 'changed' if str(path).endswith('/fd-home-drain.c') and self.proc.calls else 'same'
        with mock.patch.object(self.builder, 'R', self.root), \
                mock.patch.object(self.builder, 'DEPENDENCIES', self.deps), \
                mock.patch.object(self.builder, 'sha', side_effect=digest), \
                mock.patch.object(self.builder, 'verify', return_value={'synthetic': True}):
            with self.assertRaisesRegex(RuntimeError, 'source changed during build'):
                self.builder.build(self.work, self.proc, self.tools, time.monotonic() + 30,
                                   self.record, drain_case='stream')
        self.assertNotIn('home_probe_source_verification', self.record)

    def test_unconfirmed_process_rejects_without_publication(self):
        self.proc.fail = 'home-target-fd-client'
        with self.assertRaisesRegex(RuntimeError, 'home-target-fd-client'):
            self.build('file_prefix')
        self.assertNotIn('home_probe_target', self.record)
        self.assertEqual(len(self.proc.calls), 1)


class RustBuildSelection(unittest.TestCase):
    def test_supplied_tool_conflict_remains_rejected_before_commands(self):
        builder = module('home_engine_build')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'tools': {'rustc': {'path': '/pinned/rustc', 'sha256': 'same'}}}))
            def digest(path):
                return ('f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d'
                        if Path(path) == manifest else 'same')
            work = root / 'work'
            work.mkdir()
            proc = Process()
            with mock.patch.object(builder, 'R', root), \
                    mock.patch.object(builder, 'sha', side_effect=digest):
                with self.assertRaisesRegex(ValueError, 'supplied native tool differs: rustc'):
                    builder.build(work, proc, {'rustc': {'path': '/foreign/rustc', 'sha256': 'same'}},
                                  time.monotonic() + 30, {}, drain_case='stream')
            self.assertEqual(proc.calls, [])

    def test_actual_build_commands_and_records_bind_selected_profile(self):
        builder = module('home_engine_build')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
            manifest.parent.mkdir(parents=True)
            tools = {name: {'path': '/selected/' + name, 'sha256': 'same'} for name in
                     ('rustc', 'clippy-driver', 'lld', 'nm', 'readelf')}
            libraries = {'/selected/libcore-test.rlib': 'same',
                         '/selected/libcompiler_builtins-test.rlib': 'same'}
            manifest.write_text(json.dumps({'tools': tools, 'rust_native_libraries': libraries}))
            def digest(path):
                return ('f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d'
                        if Path(path) == manifest else 'same')
            for case in ('none', *CASES):
                work = root / case
                work.mkdir()
                proc, record = Process(), {}
                with mock.patch.object(builder, 'R', root), \
                        mock.patch.object(builder, 'sha', side_effect=digest), \
                        mock.patch.object(builder.runpy, 'run_path', return_value={'EXTRA_SOURCES': []}):
                    result = builder.build(work, proc, {}, time.monotonic() + 30,
                                           record, drain_case=case)
                selected = builder.PROFILE if case == 'none' else builder.DRAIN_PROFILE
                expected = list(selected)
                for label, argv in proc.calls:
                    if label.startswith(('rustc-', 'clippy-')):
                        actual = [argv[i + 1] for i, arg in enumerate(argv) if arg == '--cfg']
                        self.assertEqual(actual, expected)
                self.assertEqual(result['profile'], expected)
                self.assertEqual(record['home_engine_rust']['profile'], expected)
                if case == 'none':
                    self.assertEqual(set(result), {'service', 'launch', 'sources', 'flags',
                                                  'profile', 'dependencies', 'artifacts'})
                    self.assertNotIn('drain_case', record['home_engine_rust'])
                    self.assertNotIn('drain_case_id', record['home_engine_rust'])
                else:
                    self.assertEqual(result['drain_case_id'], CASES.index(case) + 1)
                    self.assertEqual(record['home_engine_rust']['drain_case'], case)
                self.assertEqual(record['home_engine_rust']['final_input_verification'], 'pass')


if __name__ == '__main__':
    unittest.main()
