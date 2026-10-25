# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_harness_runner import all_check as runner


class PublicationTests(unittest.TestCase):
    def test_atomic_replace_failure_preserves_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'results.json';path.write_bytes(b'previous')
            with patch.object(runner.os,'replace',side_effect=OSError('injected')),self.assertRaises(OSError):
                runner.publish_report(path,{'result':'pass'})
            self.assertEqual(path.read_bytes(),b'previous')
            self.assertEqual(list(Path(tmp).iterdir()),[path])
            runner.publish_report(path,{'result':'fail'})
            self.assertEqual(json.loads(path.read_text()),{'result':'fail'})

    def run_fixture(self,snapshots,publisher=None):
        with tempfile.TemporaryDirectory() as tmp:
            out=io.StringIO();err=io.StringIO();directory=Path(tmp)
            with patch.object(runner,'source_hashes',side_effect=snapshots),patch.object(runner,'run_check',return_value={'result':'pass'}) as gate,contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
                if publisher:
                    with patch.object(runner,'publish_report',side_effect=publisher):code=runner.run_suite(directory,[('one',['inert'])])
                else:code=runner.run_suite(directory,[('one',['inert'])])
            report=json.loads((directory/'results.json').read_text()) if (directory/'results.json').exists() else None
            return code,report,out.getvalue(),err.getvalue(),gate.call_count

    def test_snapshot_failure_stages(self):
        for snapshots,stage,calls in [([ValueError('bad\ninput')],'initial-snapshot',0),
                                      ([{'a':'digest'},OSError('late')],'final-snapshot',1)]:
            code,report,out,err,count=self.run_fixture(snapshots)
            self.assertEqual((code,count),(1,calls));self.assertEqual(report['error']['stage'],stage)
            self.assertFalse(report['sources_unchanged']);self.assertEqual(report['not_run'],['one'] if calls==0 else [])
            self.assertEqual(json.loads(out)['result'],'fail')
            self.assertEqual(len(report['checks']),calls)

    def test_snapshot_interrupt(self):
        code,report,out,err,count=self.run_fixture([KeyboardInterrupt()])
        self.assertEqual(code,130);self.assertEqual(report['error']['type'],'KeyboardInterrupt')
        self.assertEqual(report['source_sha256'],{});self.assertEqual(count,0)

    def test_final_publication_failure_has_no_summary(self):
        original=runner.publish_report
        def publish(path,report):
            if report['result']=='pass':raise OSError('no\nspace')
            original(path,report)
        code,report,out,err,count=self.run_fixture([{},{}],publish)
        self.assertEqual(code,1);self.assertEqual(out,'');self.assertIn('no\\nspace',err)
        self.assertEqual(report['result'],'running');self.assertEqual(count,1)

    def test_success_contract(self):
        code,report,out,err,count=self.run_fixture([{'a':'digest'},{'a':'digest'}])
        self.assertEqual(code,0);self.assertEqual(report['result'],'pass');self.assertNotIn('error',report)
        self.assertTrue(report['sources_unchanged']);self.assertEqual(report['not_run'],[])
        self.assertEqual(json.loads(out)['result'],'pass')

    def test_transient_gate_report_failure_retains_completed_gate(self):
        original=runner.publish_report;failed=False
        def publish(path,report):
            nonlocal failed
            if report['checks'] and report['result']=='running' and not failed:
                failed=True;raise OSError('transient')
            original(path,report)
        code,report,out,err,count=self.run_fixture([{}],publish)
        self.assertEqual((code,count),(1,1));self.assertEqual(len(report['checks']),1)
        self.assertEqual(report['error']['stage'],'gate-report:one')
        self.assertEqual(report['not_run'],[]);self.assertEqual(json.loads(out)['result'],'fail')
