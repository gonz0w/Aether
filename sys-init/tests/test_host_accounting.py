"""Burst terminal accounting and real exec rejection in the trusted host profile."""
from collections import Counter
import errno
import hashlib
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()


class Accounting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def runtime(self, services, commands):
        rt = HostRuntime(services, commands, cwd=self.tmp.name)
        self.addCleanup(rt.close)
        return rt

    def drain(self, rt):
        rt.until(lambda: rt.model.active is None and not rt.children and not rt.pending)

    def test_eight_terminal_children_cross_multiple_bounded_cuts(self):
        names = ['job' + str(i) for i in range(8)]
        exits = [0, 7, -signal.SIGTERM, 0, 19, -signal.SIGTERM, 0, 31]
        commands = {}
        for name, code in zip(names, exits):
            script = ('import os,signal; os.kill(os.getpid(),signal.SIGTERM)' if code < 0
                      else 'raise SystemExit(' + str(code) + ')')
            commands[name] = Command((PYTHON, '-c', script), PIN)
        rt = self.runtime([Service(n, kind='oneshot', milestone='completed',
                                   startup=1000, cleanup=1000) for n in names], commands)
        rt.start(names)
        children = list(rt.children.values())
        # Establish all terminal statuses before pumping; no assumed SIGCHLD count.
        for child, expected in zip(children, exits):
            self.assertEqual(child.wait(timeout=2), expected)
        cuts = []
        original = rt.model.batch
        def record(events=(), **kwargs):
            cuts.append(list(events))
            return original(events, **kwargs)
        with patch.object(rt.model, 'batch', side_effect=record):
            self.drain(rt)
        self.assertGreater(len(cuts), 1)
        self.assertTrue(all(len(cut) <= 4 for cut in cuts))
        observed = Counter((kind, name, generation) for cut in cuts
                           for kind, name, generation, epoch, value in cut)
        for name, code in zip(names, exits):
            expected_kind = 'fault' if code < 0 else 'exit'
            self.assertEqual(observed[('launched', name, 1)], 1)
            self.assertEqual(observed[(expected_kind, name, 1)], 1)
            self.assertEqual(observed[('cleaned', name, 1)], 1)
            state = rt.model.state[name]
            self.assertEqual(state.completed, code == 0)
            self.assertEqual(state.terminal_detail, None if code < 0 else code)
            self.assertEqual(state.terminal, 'fault' if code < 0 else ('exit-0' if code == 0 else 'exit'))
            self.assertFalse(state.owned)
            self.assertFalse(state.launch_pending)
            self.assertEqual(state.cleanup, 'complete')
        self.assertEqual(sum(observed.values()), 24)
        self.assertFalse(rt.ready)
        self.assertEqual(rt.model.operations[-1].status, 'failed')

    def test_real_exec_failures_close_pipes_and_never_admit_dependent(self):
        for body in ('not an executable image\n', '#!' + self.tmp.name + '/missing-interpreter\n'):
            with self.subTest(body=body):
                executable = Path(self.tmp.name) / 'bad-image'
                executable.write_text(body)
                executable.chmod(0o700)
                command = Command((str(executable),), hashlib.sha256(executable.read_bytes()).hexdigest())
                rt = self.runtime([Service('bad', milestone='notified-ready', startup=1000, cleanup=1000),
                                   Service('dependent', requires=(('bad', 'notified-ready'),))],
                                  {'bad': command, 'dependent': Command((PYTHON, '-c', 'pass'), PIN)})
                pipes = []
                original_pipe = os.pipe
                def record_pipe():
                    pair = original_pipe()
                    pipes.extend(pair)
                    return pair
                with patch('prototypes.host_runtime.runtime.os.pipe', side_effect=record_pipe):
                    rt.start(['dependent'])
                self.assertTrue(pipes)
                self.assertFalse(rt.children)
                self.assertFalse(rt.ready)
                self.assertEqual([event[0] for event in rt.pending], ['launch_failed'])
                for descriptor in set(pipes):
                    with self.assertRaises(OSError) as caught:
                        os.fstat(descriptor)
                    self.assertEqual(caught.exception.errno, errno.EBADF)
                self.drain(rt)
                self.assertFalse(rt.model.state['bad'].started)
                self.assertFalse(rt.model.state['bad'].owned)
                self.assertEqual(rt.model.state['bad'].reason, 'launch_failed')
                self.assertEqual(rt.model.state['dependent'].generation, 0)
                self.assertEqual(rt.model.operations[-1].status, 'failed')

    def test_changed_executable_after_construction_never_reaches_spawn(self):
        executable = Path(self.tmp.name) / 'changed'
        executable.write_text('#!/bin/sh\nexit 0\n')
        executable.chmod(0o700)
        rt = self.runtime([Service('changed', startup=1000, cleanup=1000)],
                          {'changed': Command((str(executable),),
                                              hashlib.sha256(executable.read_bytes()).hexdigest())})
        executable.write_text('#!/bin/sh\nexit 1\n')
        with patch('prototypes.host_runtime.runtime.subprocess.Popen',
                   side_effect=AssertionError('changed executable reached spawn')):
            rt.start(['changed'])
            self.drain(rt)
        self.assertEqual(rt.model.state['changed'].reason, 'launch_failed')
        self.assertFalse(rt.model.state['changed'].owned)
        self.assertEqual(rt.model.operations[-1].status, 'failed')


if __name__ == '__main__':
    unittest.main()
