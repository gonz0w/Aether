# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('extended',ROOT/'scripts/check-extended-host.py')
extended=importlib.util.module_from_spec(spec);spec.loader.exec_module(extended)
PLAN=ROOT/'docs/extended-host-plan.json'


def evidence(plan,identity,seed,implementation):
    return dict(schema='sys-init-extended-host-worker-v1',seed=seed,plan_sha256=identity,
                sources=plan['sources'],implementation=implementation,discovered=54,executed=54,
                ids=extended.ordered_ids(plan,seed),skipped=0,failures=0,errors=0,successful=True)


class ExtendedTests(unittest.TestCase):
    def test_orders_and_bad_evidence(self):
        plan,identity=extended.load_plan(PLAN);implementation=extended.implementations()
        orders=[extended.ordered_ids(plan,s) for s in plan['seeds']]
        self.assertEqual(len({tuple(o) for o in orders}),8)
        for order in orders:self.assertEqual(sorted(order),sorted(plan['test_ids']))
        value=evidence(plan,identity,plan['seeds'][0],implementation)
        extended.validate_worker(json.dumps(value).encode(),plan,identity,plan['seeds'][0],implementation)
        for change in (dict(executed=0),dict(discovered=True),dict(skipped=1),dict(ids=orders[0][:-1]),
                       dict(ids=list(reversed(orders[0]))),dict(seed='0'*64),dict(sources={}),dict(implementation={}),
                       dict(successful=False),dict(extra=1)):
            invalid=dict(value,**change)
            with self.assertRaises(ValueError):extended.validate_worker(json.dumps(invalid).encode(),plan,identity,plan['seeds'][0],implementation)
        with self.assertRaises(ValueError):extended.validate_worker(b'{',plan,identity,plan['seeds'][0],implementation)

    def test_plan_drift_and_invalid_limits(self):
        plan,_=extended.load_plan(PLAN)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'plan.json'
            for change in ('source','limits','ids','extra'):
                value=copy.deepcopy(plan)
                if change=='source':value['sources'][next(iter(value['sources']))]='0'*64
                elif change=='limits':value['limits']['workers']=True
                elif change=='ids':value['test_ids']=[]
                else:value['extra']=1
                p.write_text(json.dumps(value))
                with self.assertRaises(ValueError):extended.load_plan(p)
        with self.assertRaises(ValueError):extended.load_plan(PLAN,'0'*64)

    def test_campaign_failures_and_success(self):
        plan,identity=extended.load_plan(PLAN);implementation=extended.implementations()
        for outcome in ('pass','timeout','output-limit','interrupted','fail','invalid-evidence'):
            with self.subTest(outcome=outcome),tempfile.TemporaryDirectory() as tmp:
                directory=Path(tmp);calls=[]
                def run(name,command,root,**kwargs):
                    seed=command[command.index('--seed')+1];calls.append(seed)
                    value=evidence(plan,identity,seed,implementation)
                    if outcome=='invalid-evidence':value['skipped']=1
                    (root/(name+'.stdout')).write_text(json.dumps(value));(root/(name+'.stderr')).write_text('fixture')
                    return dict(result='pass' if outcome=='invalid-evidence' else outcome,stdout=name+'.stdout',stderr=name+'.stderr',returncode=0 if outcome=='pass' else 1)
                with patch.object(extended.aggregate,'run_check',side_effect=run),contextlib.redirect_stdout(io.StringIO()):
                    code=extended.campaign(PLAN,directory)
                report=json.loads((directory/'results.json').read_text())
                self.assertEqual(code,0 if outcome=='pass' else 130 if outcome=='interrupted' else 1)
                self.assertEqual(len(calls),8 if outcome=='pass' else 1)
                self.assertEqual(len(report['unattempted_seeds']),0 if outcome=='pass' else 7)
                self.assertEqual(report['result'],'pass' if outcome=='pass' else 'fail')

    def test_publication_failure(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(extended.aggregate,'publish_report',side_effect=OSError('injected')),contextlib.redirect_stdout(io.StringIO()) as out,contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(extended.campaign(PLAN,Path(tmp)),1);self.assertEqual(out.getvalue(),'')

    def test_replay_and_campaign_deadline(self):
        plan,identity=extended.load_plan(PLAN);implementation=extended.implementations();seed=plan['seeds'][0]
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            def run(name,command,root,**kwargs):
                (root/(name+'.stdout')).write_text(json.dumps(evidence(plan,identity,seed,implementation)))
                (root/(name+'.stderr')).write_text('')
                return dict(result='pass',stdout=name+'.stdout',stderr=name+'.stderr',returncode=0)
            with patch.object(extended.aggregate,'run_check',side_effect=run) as called,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(extended.campaign(PLAN,directory,seed),0);self.assertEqual(called.call_count,1)
            self.assertEqual(json.loads((directory/'results.json').read_text())['mode'],'replay')
        with tempfile.TemporaryDirectory() as tmp,patch.object(extended.time,'monotonic',side_effect=[0,601,602]),patch.object(extended.aggregate,'run_check') as called,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(extended.campaign(PLAN,Path(tmp)),1);called.assert_not_called()
            report=json.loads((Path(tmp)/'results.json').read_text())
            self.assertEqual(len(report['unattempted_seeds']),8)

    def test_cli_contracts(self):
        for option,code in (('--help',0),('--version',0),('--unknown',64)):
            result=subprocess.run([sys.executable,extended.__file__,option],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,code)
            self.assertTrue(result.stdout if code==0 else result.stderr)
