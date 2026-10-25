#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Deterministic lifecycle protocol controls, not remote daemon evidence."""
import json
from pathlib import Path
import runpy
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(str(ROOT / 'experiments/dash-reference/container-process.py'))


class FakeClient:
    descriptor = {'scope': 'deterministic model; no remote service'}

    def __init__(self, mode):
        self.mode = mode
        self.present = mode == 'collision'
        self.calls = []
        self.ident = 'a' * 64
        self.name = self.token = None

    def call(self, args, timeout=20):
        self.calls.append(list(args))
        code, output, complete = 0, b'', True
        if args[:2] == ['container', 'exists']:
            code = 0 if self.present else 1
            if self.mode == 'service-loss' and self.name:
                code = 125
        elif args[0] == 'create':
            self.name = args[args.index('--name') + 1]
            self.token = args[args.index('--label') + 1].split('=', 1)[1]
            self.present = True
            output = self.ident.encode() + b'\n'
            if self.mode == 'ambiguous-create':
                self.present, complete = False, False
            elif self.mode == 'ambiguous-present':
                complete = False
        elif args[:2] == ['container', 'inspect']:
            output = json.dumps([dict(Id=self.ident, Name=self.name,
                Config={'Labels': {MODULE['OWNER']: self.token
                                   if self.mode != 'foreign' else 'wrong'}})]).encode()
        elif args[0] == 'start':
            output = b'guest\n'
            if self.mode == 'guest-nonzero':
                code = 7
            elif self.mode == 'timeout':
                complete = False
            elif self.mode == 'reserved-exit':
                code = 125
        elif args[0] == 'rm':
            if self.mode == 'remove-failure':
                code = 125
            elif self.mode != 'survives-removal':
                self.present = False
        else:
            raise AssertionError(args)
        return types.SimpleNamespace(returncode=code, stdout=output,
                                     stderr=b'', record={'complete': complete})


class LifecycleTests(unittest.TestCase):
    def test_readonly_mount_and_denial(self):
        work = Path(tempfile.mkdtemp(prefix='container-mount-model-',
                                     dir=ROOT / 'build'))
        client = FakeClient('success')
        state = MODULE['run_container'](
            client, 'b' * 64, ['/bin/true'], work, inputs=work)
        self.assertTrue(state['complete'])
        create = next(c for c in client.calls if c[0] == 'create')
        self.assertIn('type=bind,src=' + str(work) + ',dst=/inputs,ro=true',
                      create)
        self.assertIn('/scratch:rw,noexec,nosuid,size=16m,mode=1777', create)
        for item in ['WITNESS=value', 'LC_ALL=C', 'PATH=/nonexistent']:
            self.assertIn(item, create)
        (work / 'calls.json').write_text(json.dumps(client.calls, indent=2))
        print('retained:', work)
        invalid = work / 'bad,ro=false'
        invalid.mkdir()
        for path in [ROOT, ROOT / 'build', invalid]:
            denied = FakeClient('success')
            with self.assertRaises(ValueError):
                MODULE['run_container'](
                    denied, 'b' * 64, ['/bin/true'], work, inputs=path)
            self.assertFalse(denied.calls)

    def test_generator_mount_boundary(self):
        tree = Path(tempfile.mkdtemp(prefix='generator-mount-model-',
                                     dir=ROOT / 'build'))
        target = tree / 'obj'
        target.mkdir()
        client = FakeClient('success')
        state = MODULE['run_container'](
            client, 'b' * 64, ['/bin/true'], tree,
            generator_root=tree, generator_cwd=target)
        self.assertTrue(state['complete'])
        create = next(c for c in client.calls if c[0] == 'create')
        self.assertIn('type=bind,src=' + str(tree) + ',dst=' + str(tree)
                      + ',ro=true', create)
        self.assertIn('type=bind,src=' + str(target) + ',dst=' + str(target)
                      + ',rw=true', create)
        self.assertEqual(create[create.index('--workdir') + 1], str(target))
        (tree / 'calls.json').write_text(json.dumps(client.calls, indent=2))
        print('retained:', tree)
        for kwargs in [dict(generator_root=tree),
                       dict(generator_root=tree, generator_cwd=tree),
                       dict(generator_root=tree, generator_cwd=ROOT),
                       dict(generator_root=tree, generator_cwd=target,
                            inputs=tree)]:
            denied = FakeClient('success')
            with self.assertRaises(ValueError):
                MODULE['run_container'](
                    denied, 'b' * 64, ['/bin/true'], tree, **kwargs)
            self.assertFalse(denied.calls)

    def test_protocol_outcomes(self):
        for mode in ['success', 'guest-nonzero', 'timeout', 'foreign',
                     'service-loss', 'remove-failure', 'ambiguous-create',
                     'collision', 'survives-removal', 'reserved-exit',
                     'ambiguous-present']:
            with self.subTest(mode=mode):
                work = Path(tempfile.mkdtemp(prefix='container-model-',
                                             dir=ROOT / 'build'))
                client = FakeClient(mode)
                state = MODULE['run_container'](
                    client, 'b' * 64, ['/bin/true'], work)
                (work / 'calls.json').write_text(json.dumps(client.calls,
                                                           indent=2) + '\n')
                print('retained:', work)
                self.assertEqual(state['complete'],
                                 mode in ('success', 'guest-nonzero'))
                if mode == 'timeout':
                    self.assertEqual(state['cleanup'], 'absent')
                    self.assertFalse(client.present)
                if mode in ('ambiguous-create', 'ambiguous-present'):
                    self.assertEqual(state['cleanup'], 'unresolved-create')
                    self.assertFalse(any(c[0] == 'start' for c in client.calls))
                if mode in ('foreign', 'collision'):
                    self.assertFalse(any(c[0] == 'rm' for c in client.calls))
                    self.assertTrue(client.present)
                if mode in ('service-loss', 'remove-failure',
                            'survives-removal'):
                    self.assertEqual(state['cleanup'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
