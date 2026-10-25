import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from prototypes.host_runtime.descriptors import Prepared, parse
from prototypes.runtime_model.model import Rejected

class Descriptors(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'job.json'
        executable=str(Path(sys.executable).resolve())
        self.d=dict(schema='aether-service-experiment-v1',id='job',package='fixture',executable_sha256=hashlib.sha256(Path(executable).read_bytes()).hexdigest(),target='host-posix-experiment-v1',argv=[executable,'-c','pass'],environment={},kind='oneshot',requires={},after=[],readiness='completed',restart=dict(mode='never',retries=0,delay_ms=1),authority_requests=[])
    def write(self): self.path.write_text(json.dumps(self.d))
    def test_actual_descriptor_launch(self):
        self.write(); rt=Prepared([self.path]).activate(cwd=self.tmp.name); self.addCleanup(rt.close)
        rt.start(['job']); rt.until(lambda: not rt.children and not rt.pending)
        self.assertTrue(rt.model.state['job'].completed)
    def test_stale_preparation(self):
        self.write(); prepared=Prepared([self.path]); self.d['argv'][-1]='raise SystemExit(5)'; self.write()
        with self.assertRaises(Rejected): prepared.activate(cwd=self.tmp.name)
    def test_duplicate_nested_unknown_and_nonfinite(self):
        raw=json.dumps(self.d)
        for candidate in [raw.replace('"environment": {}','"environment": {"X":"a","X":"b"}'),raw[:-1]+',"unknown":1}',raw.replace('"delay_ms": 1','"delay_ms": NaN'),'['*10000,b'x'*65537]:
            with self.subTest(candidate=str(candidate)[:40]),self.assertRaises(Rejected): parse(candidate if isinstance(candidate,bytes) else candidate.encode())
    def test_unsupported_profile_is_not_silently_reduced(self):
        for field,value in [('target','aether'),('authority_requests',['root']),('argv','echo bad'),('readiness','started'),('restart',dict(mode='never',retries=0,delay_ms=0)),('environment',{'1bad':'x'})]:
            d=copy.deepcopy(self.d); d[field]=value
            with self.subTest(field=field),self.assertRaises(Rejected): parse(json.dumps(d).encode())
    def test_graph_rejected_before_launch(self):
        for req in [{'missing':'completed'},{'job':'completed'}]:
            self.d['requires']=req; self.write()
            with self.assertRaises(Rejected): Prepared([self.path])
    def test_shell_shaped_argument_is_inert(self):
        self.d['argv']=[self.d['argv'][0],'-c','import sys; assert sys.argv[1] == "$(touch bad)"','$(touch bad)']; self.write()
        rt=Prepared([self.path]).activate(cwd=self.tmp.name); self.addCleanup(rt.close)
        rt.start(['job']); rt.until(lambda: not rt.children and not rt.pending)
        self.assertTrue(rt.model.state['job'].completed); self.assertFalse((Path(self.tmp.name)/'bad').exists())
