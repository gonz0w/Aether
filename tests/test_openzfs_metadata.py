# SPDX-License-Identifier: BSD-2-Clause
"""Read-only engine metadata: real bodies, API faults, layout and native imports."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from openzfs_elapsed import CURRENT, route
from fs_launch_intake import intake

OWNED = ROOT/'user/storage/openzfs-volume'


class Metadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-zpl-metadata-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.out = Path(cls.temporary.name)
        cls.clang = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')
        cls.sdk = subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        cls.body = '\n'.join(l for l in (OWNED/'zpl-metadata.c').read_text().splitlines() if not l.startswith('#include'))+'\n'
        reader = '\n'.join(l for l in (OWNED/'zpl-read.c').read_text().splitlines() if not l.startswith('#include'))+'\n'
        (cls.out/'zpl-adapter.inc').write_text(reader)
        cls.binary = cls.compile(cls.body, 'metadata')

    @classmethod
    def compile(cls, body, name):
        (cls.out/'metadata.inc').write_text(body)
        binary = cls.out/name
        result = subprocess.run([str(cls.clang),'-isysroot',cls.sdk,'-std=gnu11','-O2',
            '-Wall','-Wextra','-Werror','-I'+str(cls.out),'-I'+str(OWNED),
            ROOT/'tests/fixtures/openzfs_zpl_metadata.c','-o',binary],capture_output=True,text=True,timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout+result.stderr)
        return binary

    def mode(self, mode=0, fault=0, binary=None, expected=0):
        result = subprocess.run([str(binary or self.binary),str(mode),str(fault)],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        if expected == 95: self.assertIn('HOST METADATA oracle95',result.stderr)
        return result.stdout

    def test_exact_regular_directory_links_owner_flags_and_signed_times(self):
        for mode in (0,1,2,3,4,5,25): self.mode(mode)

    def test_arguments_stale_type_format_parent_links_and_every_time_bound(self):
        for mode in range(6,25): self.mode(mode)

    def test_every_reachable_lookup_failure_clears_partial_output_and_releases_sa(self):
        calls = int(re.search(r'calls=(\d+)',self.mode())[1])
        self.assertEqual(calls,5)
        for fault in range(1,calls+1): self.mode(fault=fault)

    def test_named_compiling_omissions_fail_semantic_metadata_oracle(self):
        cases = (
            ('stale','metadata.node.generation != generation','((void)generation, 0)',10,0),
            ('clear','memset(out, 0, sizeof(*out));','/* omitted clear */',6,0),
            ('release','sa_handle_destroy(handle);','/* omitted release */',0,0),
            ('time','times[i]->nanoseconds >= UINT64_C(1000000000)','((void)times[i], 0)',16,0),
            ('links','!metadata.links','0',23,0),
            ('xattr','metadata.flags & ZFS_XATTR','0',24,0),
            ('partial-publication','sa_handle_destroy(handle);','*out = metadata;\n    sa_handle_destroy(handle);',0,5),
            ('owner-truncation','*out = metadata;','metadata.uid = (uint32_t)metadata.uid;\n    *out = metadata;',3,0),
        )
        for name,old,new,mode,fault in cases:
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old),1)
                binary = self.compile(self.body.replace(old,new,1),name)
                self.mode(mode,fault,binary,95)

    def test_pinned_native_headers_layout_symbols_imports_dependencies_and_frames(self):
        receipt = json.loads((CURRENT/'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name']=='input-176-checked')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        llvm = Path(prefix[0]).parent
        prefix += ['-isystem',str(llvm.parent/'lib/clang/21/include'),'-I'+str(OWNED),
                   '-std=gnu11','-Wall','-Wextra','-Werror','-fstack-usage']
        imports, symbols = {}, {}
        for name in ('zpl-directories','zpl-metadata'):
            obj, deps = self.out/(name+'.o'), self.out/(name+'.d')
            argv = prefix+['-MD','-MF',str(deps),'-c',str(OWNED/(name+'.c')),'-o',str(obj)]
            result = subprocess.run(argv,capture_output=True,text=True,timeout=180)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            imports[name] = set(subprocess.check_output([llvm/'llvm-nm','-u',obj],text=True).split())
            symbols[name] = {line.split()[-1] for line in subprocess.check_output([llvm/'llvm-nm','--defined-only','--extern-only',obj],text=True).splitlines() if line.strip()}
            pins = json.loads((CURRENT/'current-inputs.json').read_text())['files']
            inputs = {}
            for value in deps.read_text().split(':',1)[1].replace('\\\n',' ').split():
                p = Path(value); h = hashlib.sha256(p.read_bytes()).hexdigest(); inputs[str(p)] = h
                if p.is_relative_to(CURRENT): self.assertEqual(pins[str(p.relative_to(CURRENT))],h)
            frames = obj.with_suffix('.su').read_text()
            self.assertNotIn('dynamic',frames)
            self.assertLessEqual(max(int(l.split('\t')[1]) for l in frames.splitlines()),8192)
            print('METADATA NATIVE '+json.dumps(dict(argv=argv,object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
                dependency_sha256=inputs,local_frames=frames,scope='Unlinked native headers and local frames only, not disk/native service or complete call-stack proof')))
        self.assertEqual(imports['zpl-metadata'],imports['zpl-directories'])
        self.assertEqual(symbols['zpl-metadata']-symbols['zpl-directories'],{'aether_zpl_getattr'})
        self.assertFalse(symbols['zpl-directories']-symbols['zpl-metadata'])
        # The fixed Rust-facing record remains17 eight-byte fields, with no
        # packed pointers or changed original node layout; native compilation
        # enforces the header's explicit offsets/size assertions.
        self.assertIn('sizeof(aether_zpl_metadata) == 136',(OWNED/'zpl-metadata.h').read_text())

    def test_current_sealed_engine_inputs_and_abi_remain_unchanged(self):
        self.assertEqual(intake(ROOT/'.deps/fs-launch-2026-10-20-v4')['members'],30)


if __name__=='__main__': unittest.main()
