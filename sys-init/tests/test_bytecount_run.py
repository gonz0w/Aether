# SPDX-License-Identifier: BSD-2-Clause
"""Closed bytecount output and cleanup oracles."""
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
recipe = runpy.run_path(str(SCRIPTS / 'run-bytecount.py'))
serial = runpy.run_path(str(SCRIPTS / 'persistent_zsh_serial.py'))
HOST = dict(status='complete', terminal='halt', host_stop_confirmed=True,
            group_absent=True, stdout_eof=True, stderr_eof=True,
            capture_complete=True, input_bytes=0)
RAW = b''.join(
    f'NATIVE terminal slot={i} generation=1 kind=1 detail=0\n'
    f'NATIVE CLEANUP v=1 slot={i} generation=1 phase=7 selected=6 pages=640 reclaimed={i+1}\n'.encode()
    for i in range(3))
RAW += (b'AETHER BYTECOUNT OWNER v=1 requests=65 child_status=0 exec_ready=1 child_reclaimed=1 '
        b'file_exec_bytes=42904 output_verified=1 mode_cleanup=0\n'
        b'AETHER NATIVE BLOCK PASS\nNATIVE init halted ticks=20 idle=5 reclaimed=3\n')


class BytecountTests(unittest.TestCase):
    def test_exact_output_and_cleanup(self):
        self.assertEqual(recipe['observe'](RAW, HOST, 'seed')['output_hex'], '360a')

    def test_output_or_host_gaps_reject(self):
        for old, new in [(b'output_verified=1', b'output_verified=0'),
                         (b'child_status=0', b'child_status=23'),
                         (b'file_exec_bytes=42904', b'file_exec_bytes=3548'),
                         (b'detail=0', b'detail=1'), (b'reclaimed=3', b'reclaimed=2')]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                recipe['observe'](RAW.replace(old, new), HOST, 'cold')
        for field in ('host_stop_confirmed', 'group_absent', 'stdout_eof', 'stderr_eof'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                recipe['observe'](RAW, dict(HOST, **{field: False}), 'cold')

    def test_native_ready_marker_consumes_no_input(self):
        class Transfer:
            record = dict(input_stages=[])
            overflow = False
            uart = bytearray(b'NATIVE MEMORY admitted slot=1 generation=1 used=30\n')
            sources = [1]
            pending = b''
            child = object()

            def pump(self, until, operator_input):
                assert not operator_input and not self.pending
                self.uart.extend(b'NATIVE init halted ticks=1 idle=1 reclaimed=3\nAETHER NATIVE BLOCK PASS\n')
        transfer = Transfer()
        with patch.dict(serial['run_session'].__globals__, exited=lambda _: False):
            result = serial['run_session'](transfer, serial['time'].monotonic(),
                       serial['time'].monotonic()+120, False, False, (), [],
                       b'NATIVE MEMORY admitted slot=1 generation=1 ')
        self.assertEqual(result, 'halt')
        self.assertIn('first_prompt_offset', transfer.record)


if __name__ == '__main__':
    unittest.main()
