# SPDX-License-Identifier: BSD-2-Clause
"""Host descriptor contracts whose validation stages and limits matter to callers."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from prototypes.host_runtime.descriptors import Prepared, parse
from prototypes.runtime_model.model import Rejected
import test_host_descriptors as descriptor_tests


class DescriptorContract(unittest.TestCase):
    setUp = descriptor_tests.Descriptors.setUp
    write = descriptor_tests.Descriptors.write

    def raw(self, data=None):
        return json.dumps(self.d if data is None else data).encode()

    def test_byte_and_scalar_boundaries(self):
        raw = self.raw()
        parse(raw + b' ' * (65536 - len(raw)))
        for bad in [raw + b' ' * (65537 - len(raw)), raw.decode(), b'', b'\xff']:
            with self.subTest(kind=type(bad).__name__), self.assertRaises(Rejected):
                parse(bad)
        for field in ('retries', 'delay_ms'):
            d = copy.deepcopy(self.d)
            d['restart'][field] = True
            with self.assertRaises(Rejected):
                parse(self.raw(d))
        for value, accepted in [('é' * 2048, True), ('é' * 2049, False), ('\ud800', False)]:
            d = copy.deepcopy(self.d)
            d['argv'].append(value)
            if accepted:
                parse(self.raw(d))
            else:
                with self.assertRaises(Rejected):
                    parse(self.raw(d))

    def test_validation_is_staged(self):
        for field, value in [('id', 'Upper.Case'), ('argv', ['relative']),
                             ('environment', {'AETHER_READY_FD': '7'})]:
            with self.subTest(field=field):
                d = copy.deepcopy(self.d)
                d[field] = value
                parse(self.raw(d))  # syntax-valid; not prepared or launchable
                self.path.write_bytes(self.raw(d))
                with self.assertRaises(Rejected):
                    Prepared([self.path])

    def test_preparation_and_activation_do_not_launch_and_bytes_are_pinned(self):
        self.write()
        with patch('prototypes.host_runtime.runtime.subprocess.Popen',
                   side_effect=AssertionError('unexpected process launch')):
            prepared = Prepared([self.path])
            first = prepared.activate(cwd=self.tmp.name)
            second = prepared.activate(cwd=self.tmp.name)
            try:
                self.assertFalse(first.children)
                self.assertNotEqual(first.model.epoch, second.model.epoch)
            finally:
                first.close()
                second.close()
            self.path.write_bytes(self.path.read_bytes() + b' ')
            with self.assertRaisesRegex(Rejected, 'stale prepared'):
                prepared.activate(cwd=self.tmp.name)

    def test_graph_size_edges_and_fixed_budgets(self):
        service, _ = parse(self.raw())
        self.assertEqual((service.startup, service.stop, service.cleanup), (1000, 1000, 1000))
        paths = []
        for index in range(8):
            d = copy.deepcopy(self.d)
            d['id'] = 's' + str(index)
            path = Path(self.tmp.name) / (d['id'] + '.json')
            path.write_bytes(self.raw(d))
            paths.append(path)
        Prepared(paths)
        with self.assertRaisesRegex(Rejected, 'graph size'):
            Prepared(paths + [paths[0]])
        # Eight valid services, but a 28-edge acyclic dependency graph is too large.
        for index, path in enumerate(paths):
            d = json.loads(path.read_bytes())
            d['requires'] = {'s' + str(p): 'completed' for p in range(index)}
            path.write_bytes(self.raw(d))
        with self.assertRaisesRegex(Rejected, 'edge bound'):
            Prepared(paths)

    def test_explicit_environment_overrides_defaults_in_real_child(self):
        self.d['environment'] = {'PATH': 'fixture-path', 'LC_ALL': 'POSIX', 'EMPTY': ''}
        self.d['argv'] = [self.d['argv'][0], '-c',
            'import os,sys; sys.exit(0 if (os.environ.get("PATH"), '
            'os.environ.get("LC_ALL"), os.environ.get("EMPTY"), '
            'os.environ.get("AETHER_READY_FD")) == '
            '("fixture-path", "POSIX", "", None) else 9)']
        self.write()
        runtime = Prepared([self.path]).activate(cwd=self.tmp.name)
        try:
            runtime.start(['job'])
            runtime.until(lambda: not runtime.children and not runtime.pending)
            self.assertTrue(runtime.model.state['job'].completed)
        finally:
            runtime.close()

    def test_documentation_example_executes_and_cleans_up(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / 'docs/examples/host-descriptor.py')],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'host descriptor example: pass\n')
        self.assertFalse(result.stderr)
