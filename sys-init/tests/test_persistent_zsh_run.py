# SPDX-License-Identifier: BSD-2-Clause
"""Focused checks for the persistent Zsh launch and cleanup receipts."""
from pathlib import Path
import runpy
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
RECIPE = runpy.run_path(str(SCRIPTS / 'run-persistent-zsh.py'))
observe = RECIPE['observe']
HOST = dict(status='complete', host_stop_confirmed=True, group_absent=True,
            stdout_eof=True, stderr_eof=True, input_bytes=0)
ENGINE = b'NATIVE MEMORY admitted slot=0 generation=1 used=1331 remaining=6861\n'
APP = b'NATIVE MEMORY admitted slot=1 generation=1 used=321 remaining=319\n'
FAILURE = ENGINE + (
    b'NATIVE terminal slot=0 generation=1 kind=1 detail=5\n'
    b'NATIVE CLEANUP v=1 slot=0 generation=1 phase=7 selected=6 pages=8192 reclaimed=1\n'
    b'AETHER PANIC: native supervisor terminated\n'
)


class ReceiptTests(unittest.TestCase):
    def test_refusal_reports_guest_and_host_cleanup_separately(self):
        result = observe(FAILURE, dict(HOST, terminal='startup-failure'), 'failure', False)
        self.assertTrue(result['engine_reclaimed'])
        self.assertFalse(result['shell_admitted'])
        self.assertEqual(result['export'], 'unverified')

    def test_app_admission_invalidates_refusal(self):
        with self.assertRaisesRegex(ValueError, 'without shell admission'):
            observe(ENGINE + APP + FAILURE[len(ENGINE):],
                    dict(HOST, terminal='startup-failure'), 'failure', False)

    def test_missing_host_eof_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, 'cleanup unknown'):
            observe(FAILURE, dict(HOST, terminal='startup-failure', stderr_eof=False),
                    'failure', False)

    def test_no_qemu_network_or_monitor(self):
        args = RECIPE['command']('qemu', 'image', 'code', 'variables', 'disk')
        self.assertEqual(args[args.index('-nic') + 1], 'none')
        self.assertEqual(args[args.index('-monitor') + 1], 'none')
        self.assertEqual(args[args.index('-serial') + 1], 'stdio')


if __name__ == '__main__':
    unittest.main()
