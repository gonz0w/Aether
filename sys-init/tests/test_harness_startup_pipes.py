# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from test_harness_runner import all_check as runner


class StartupPipeTests(unittest.TestCase):
    def test_output_root_file_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'not-a-dir';p.write_text('keep')
            result=subprocess.run([sys.executable,runner.__file__,'--output-root',str(p)],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,1);self.assertEqual(result.stdout,'')
            self.assertIn('output directory unavailable',result.stderr);self.assertNotIn('Traceback',result.stderr)
            self.assertEqual(p.read_text(),'keep')

    def test_startup_interrupt(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(sys,'argv',['checks','--output-root',tmp]),patch.object(runner.tempfile,'mkdtemp',side_effect=KeyboardInterrupt()),contextlib.redirect_stdout(io.StringIO()) as out,contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(runner.main(),130);self.assertEqual(out.getvalue(),'')
            self.assertIn('output directory unavailable',err.getvalue())

    def test_real_closed_summary_and_progress_pipes(self):
        for stream in ('stdout','stderr'):
            with self.subTest(stream=stream),tempfile.TemporaryDirectory() as tmp:
                code=f'''import importlib.util,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('runner',{runner.__file__!r})
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
r.source_hashes=lambda: {{}}
r.run_check=lambda *a: {{'result':'pass'}}
sys.stdin.read(1)
raise SystemExit(r.run_suite(Path({tmp!r}),[('one',['inert']),('two',['inert'])]))
'''
                child=subprocess.Popen([sys.executable,'-c',code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                getattr(child,stream).close()
                setattr(child,stream,None)
                child.stdin.write('x');child.stdin.close();child.stdin=None
                try:
                    outputs=child.communicate(timeout=5)
                finally:
                    if child.poll() is None:child.kill();child.wait()
                text=outputs[1 if stream=='stdout' else 0]
                self.assertEqual(child.returncode,1)
                self.assertNotIn('Traceback',text);self.assertNotIn('Exception ignored',text)
                report=json.loads((Path(tmp)/'results.json').read_text())
                if stream=='stdout':
                    self.assertEqual(report['result'],'pass');self.assertEqual(len(report['checks']),2)
                    self.assertIn('summary delivery failed',text)
                else:
                    self.assertEqual(report['result'],'fail');self.assertEqual(len(report['checks']),1)
                    self.assertEqual(report['not_run'],['two']);self.assertEqual(report['error']['stage'],'gate-progress:one')
                    self.assertEqual(json.loads(text)['result'],'fail')

    def test_unavailable_diagnostic_stream(self):
        stream=io.StringIO()
        with patch.object(sys,'stderr',stream),patch.object(stream,'write',side_effect=BrokenPipeError()),patch.object(runner,'silence_failed_stream') as silence:
            runner.report_diagnostic('test',OSError('bad\npath'))
            silence.assert_called_once_with(stream)
