# SPDX-License-Identifier: BSD-2-Clause
"""Semantic counterexamples for the host serial-session oracle."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from console_smoke import check_pipeline_console


def transcript():
    # Independent expected workload bytes, including long stdout and stderr.
    session = (b'$ ' + b'0123456789' * 8 + b'\n' +
               b'stderr-0123456789' * 4 + b'\n$ pipe data\n$ after-' +
               b'9876543210' * 8 + b'\n')
    data = b'AETHER M1 PASS\n' + session * 3
    for generation in (1, 2, 3):
        for slot in range(5):
            data += f'NATIVE terminal slot={slot} generation={generation} kind=1 detail=0\n'.encode()
    return data + b'NATIVE supervisor result=100 reclaimed=15\nAETHER NATIVE CONSOLE PASS\n'


class PipelineConsoleTests(unittest.TestCase):
    def test_valid_and_interleaved_native_marker(self):
        data = transcript()
        check_pipeline_console(data)
        check_pipeline_console(data.replace(b'pipe data', b'pipe NATIVE MEMORY admitted slot=4 generation=1 used=25 remaining=103\ndata', 1))

    def test_changed_missing_and_extra_stream_bytes(self):
        data = transcript()
        for changed in (data.replace(b'pipe data', b'Pipe data', 1),
                        data.replace(b'stderr-', b'', 1),
                        data.replace(b'\n$ pipe', b'\nextra\n$ pipe', 1)):
            with self.subTest(changed=changed[:90]):
                with self.assertRaisesRegex(RuntimeError, '^pipeline UART output mismatch$'):
                    check_pipeline_console(changed)

    def test_missing_duplicate_or_failed_child(self):
        data = transcript()
        terminal = b'NATIVE terminal slot=2 generation=1 kind=1 detail=0\n'
        for changed in (data.replace(terminal, b''), data + terminal,
                        data.replace(terminal, terminal.replace(b'detail=0', b'detail=1'))):
            with self.assertRaisesRegex(RuntimeError, '^pipeline terminal history mismatch$'):
                check_pipeline_console(changed)

    def test_markers_do_not_replace_cleanup_or_prompts(self):
        data = transcript()
        for changed, reason in ((data.replace(b'reclaimed=15', b'reclaimed=14'), 'cleanup'),
                                (data.replace(b'$ ', b'', 1), 'command/prompt'),
                                (data + b'AETHER NATIVE CONSOLE PASS\n', 'completion marker missing')):
            with self.assertRaisesRegex(RuntimeError, 'pipeline ' + reason):
                check_pipeline_console(changed)

    def test_panic_cannot_be_a_positive(self):
        with self.assertRaisesRegex(RuntimeError, '^pipeline unexpected panic$'):
            check_pipeline_console(b'AETHER PANIC: broken\n' + transcript())
