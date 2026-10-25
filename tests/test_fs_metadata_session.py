# SPDX-License-Identifier: BSD-2-Clause
"""Explicit AF07 SESSION selection, real controller fit and bounded oracle capture."""
import copy
import hashlib
import json
import inspect
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_session as session
from openzfs_fs_metadata_service import client
import test_fs_session as existing


class MetadataSession(unittest.TestCase):
    def command(self,args,status=0):
        row=subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,text=True,timeout=60)
        self.assertEqual(row.returncode,status,row.stdout+row.stderr)
        return row.stdout+row.stderr

    def test_real_metadata_controller_exact_adaptation_strict_compile_fit_and_stack(self):
        with tempfile.TemporaryDirectory(prefix='aether-af07-session-host-') as folder:
            output=Path(folder)
            session.adapt_clients(output,metadata_service=True)
            original=(ROOT/'user/storage/service-runtime/fs-directories-client.rs').read_text()
            anchor='                check(token == 8 && txg > 790);'
            metadata_anchor=anchor.replace('token == 8','token == 9')
            expected=client(original).replace(metadata_anchor,metadata_anchor+'\n                super::super::witness(txg);')
            self.assertEqual((output/'directories.rs').read_text(),expected)
            cfg=[arg for name in session.CFG for arg in ('--cfg',name)]
            base=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-Dwarnings',
                  '-Dunsafe_op_in_unsafe_fn','-Adead_code','-Copt-level=z','-Cpanic=abort','-Crelocation-model=static',
                  '-Clto=fat','-Ccodegen-units=1','-Cjump-tables=no','-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld',*cfg,output/'owner.rs']
            self.command(base+['-Clink-arg=--oformat=binary','-o',output/'owner.raw'])
            self.command(base+['-o',output/'owner.elf'])
            self.assertLessEqual((output/'owner.raw').stat().st_size,8192)
            self.assertGreater((output/'owner.raw').stat().st_size,0)
            from fs_init_intake import intake
            admitted=intake(output/'owner.elf',output/'owner.raw',session.sha(output/'owner.elf'),session.sha(output/'owner.raw'))
            self.assertLessEqual(admitted['stack']['entry_stack_bytes'],4096)
            # The default source adaptation is unchanged after the explicit variant.
            session.adapt_clients(output)
            self.assertEqual((output/'directories.rs').read_text(),original.replace(anchor,anchor+'\n                super::super::witness(txg);'))

    def test_exact_clock_flood_summary_preserves_storage_wait_oracle_errors_and_unknowns(self):
        original=existing.FilesystemComposition().trace()
        clocks=('NATIVE CLOCK park task=6 start=123 deadline=456\nNATIVE CLOCK timeout task=6 now=456 elapsed=333\n')*2000
        text=clocks+original
        self.assertFalse(session.machine_witness(text)['selection_complete'])
        capture=session.metadata_oracle_witness(text)
        self.assertTrue(capture['selection_complete'])
        self.assertEqual(capture['omitted_clock_events'],dict(lines=4000,sha256=hashlib.sha256(clocks.encode()).hexdigest()))
        self.assertEqual(capture['source_selection'],dict(total_lines=session.machine_witness(text)['total_lines'],sha256=hashlib.sha256(text.encode()).hexdigest()))
        selected=session.metadata_oracle_text(capture)
        self.assertEqual(session.writer_trace(selected),session.writer_trace(original))
        self.assertIn('NATIVE STORAGE WAIT slot=6 generation=0 phase=wake status=0',selected)
        failures='NATIVE CLOCK timeout task=6 now=456 elapsed=333 error=5\nNATIVE CLOCK unknown field=1\nAETHER PANIC: bad\n'
        self.assertEqual(session.metadata_oracle_witness(failures)['lines'],failures.splitlines())
        with self.assertRaises(ValueError):session.writer_trace(selected+failures)
        overflow=session.metadata_oracle_witness(('NATIVE STORAGE WAIT slot=6 generation=0 phase=park status=-5\n')*2000)
        self.assertFalse(overflow['selection_complete'])
        self.assertEqual(overflow['omitted_clock_events']['lines'],0)

    def test_lossless_wait_dictionary_replays_large_complete_trace_and_failed_prefix_exactly(self):
        original=existing.FilesystemComposition().trace()
        pairs=''.join(f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0\n'
                      for slot,generation in ((0,1),(6,0)) for phase in ('park','wake'))
        text=original.replace('NATIVE init halted ',pairs*650+'NATIVE init halted ')
        self.assertFalse(session.machine_witness(text)['selection_complete'])
        capture=session.metadata_oracle_witness(text)
        self.assertTrue(capture['selection_complete'])
        self.assertLess(capture['retained_utf8_bytes'],65536)
        self.assertEqual(session.metadata_oracle_text(capture),text)
        self.assertEqual(session.writer_trace(session.metadata_oracle_text(capture)),session.writer_trace(text))
        self.assertGreater(session.writer_trace(text)['primary_channel_waits'],1300)
        failed=json.loads((ROOT/'docs/evidence/fs-af07-operational-attempt1-2026-10-21.json').read_text())
        for text in ('\n'.join(failed['serial']['writer']['machine_witness']['lines'])+'\n',failed['serial']['writer']['tail']):
            capture=session.metadata_oracle_witness(text)
            filtered=''.join(line+'\n' for line in text.splitlines() if not re.fullmatch(
                r'NATIVE CLOCK park task=\d+ start=\d+ deadline=\d+|NATIVE CLOCK timeout task=\d+ now=\d+ elapsed=\d+',line))
            expected='\n'.join(session.machine_witness(filtered)['lines'])+'\n'
            self.assertEqual(session.metadata_oracle_text(capture),expected)
            # Prefix/tail remain incomplete observations of the failed execution.
            with self.assertRaises(ValueError):session.writer_trace(expected)

    def test_wait_dictionary_collisions_unknowns_errors_and_corrupt_evidence_reject(self):
        raw='NATIVE SW 0P\nNATIVE RAW NATIVE SW 6W\nNATIVE STORAGE WAIT slot=1 generation=1 phase=park status=0\nNATIVE STORAGE WAIT slot=0 generation=1 phase=wake status=-5\nAETHER PANIC: bad\n'
        capture=session.metadata_oracle_witness(raw)
        self.assertEqual(session.metadata_oracle_text(capture),raw)
        self.assertIn('NATIVE RAW NATIVE SW 0P',capture['lines'])
        valid=session.metadata_oracle_witness(existing.FilesystemComposition().trace())
        for key,value in (('format','old'),('selection_complete',False),('ceiling_utf8_bytes',131072),
                          ('retained_utf8_bytes',1),('total_lines',1),('total_lines','bad'),('full_selection_sha256','0'*64),
                          ('decoded_selection',{}),('decoded_selection',[]),('source_selection',{}),
                          ('omitted_clock_events',{'lines':-1}),('lines',['NATIVE X\nY']),
                          ('lines',[None]),('lines',['NATIVE '+('x'*65536)])):
            bad=copy.deepcopy(valid);bad[key]=value
            with self.subTest(key=key,value=str(value)[:30]),self.assertRaises(ValueError):session.metadata_oracle_text(bad)
        for transform in (lambda lines:lines.remove('NATIVE SW 0W'),lambda lines:lines.reverse()):
            bad=copy.deepcopy(valid);transform(bad['lines'])
            with self.assertRaises(ValueError):session.metadata_oracle_text(bad)
        source=inspect.getsource(session.metadata_oracle_witness)
        self.assertEqual(source.count('encoded.append(_WAIT_ENCODE[line])'),1)
        scope=dict(session.__dict__)
        exec(compile(source.replace('encoded.append(_WAIT_ENCODE[line])','None'),'<omitted-wait-capture>','exec'),scope)
        omitted=scope['metadata_oracle_witness'](existing.FilesystemComposition().trace())
        with self.assertRaisesRegex(ValueError,'source/clock|decoded oracle'):session.metadata_oracle_text(omitted)
        broken=session.metadata_oracle_witness(existing.FilesystemComposition().trace().replace('phase=wake','phase=park'))
        with self.assertRaises(ValueError):session.writer_trace(session.metadata_oracle_text(broken))

    def test_invalid_combination_seal_and_path_reject_before_any_preparation(self):
        candidate=ROOT/'.deps/fs-launch-af07-host-unselected'
        cases=[dict(metadata_candidate=(candidate,'0'*64),controller_16k=True),
               dict(metadata_candidate=(candidate,'0'*64),sys_init=True),
               dict(metadata_candidate=(candidate,'0'*64),sys_init_checks=True),
               dict(metadata_candidate=(candidate,'bad')),dict(metadata_candidate=(candidate,None)),
               dict(metadata_candidate=(candidate,)),dict(metadata_candidate=(Path('/tmp/unowned'),'0'*64))]
        with patch.object(session.tempfile,'mkdtemp',side_effect=AssertionError('preparation forbidden')):
            for kwargs in cases:
                with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):session.campaign(**kwargs)

    def test_failed_preparation_captures_complete_early_af07_records_and_disposes(self):
        import fs_metadata_launch
        with tempfile.TemporaryDirectory(prefix=session.PREFIX,dir=ROOT/'zig-out') as folder:
            output=Path(folder);(output/'writer').mkdir()
            text=existing.FilesystemComposition().trace()+('firmware\n'*1000)
            (output/'writer/native-serial.log').write_text(text)
            with patch.object(session.tempfile,'mkdtemp',return_value=folder), \
                 patch.object(fs_metadata_launch,'intake',side_effect=ValueError('HOST_PREPARATION_STOP')), \
                 patch.object(session,'run') as guest:
                with self.assertRaisesRegex(ValueError,'HOST_PREPARATION_STOP'):
                    session.campaign(metadata_candidate=(ROOT/'.deps/fs-launch-af07-host-unselected','0'*64))
                guest.assert_not_called()
            row=json.loads((output/'results.json').read_text())
            self.assertFalse(row['native_attempted'])
            self.assertEqual(row['status'],'failed')
            self.assertEqual(row['metadata_protocol'],'AFSRPC07')
            capture=row['serial']['writer']['machine_witness']
            self.assertTrue(capture['selection_complete'])
            session.writer_trace(session.metadata_oracle_text(capture))
            self.assertEqual([p.name for p in output.iterdir()],['results.json'])

    def test_cli_rejects_ambiguous_metadata_selections_without_starting(self):
        for arguments,status in ((['--help'],0),(['--version'],0),(['--metadata-engine','.deps/fs-launch-af07-x'],64),
                (['--metadata-seal','0'*64],64),(['--metadata-engine','.deps/fs-launch-af07-x','--metadata-seal','bad'],64),
                (['--metadata-engine','.deps/fs-launch-af07-x','--metadata-seal','0'*64,'--sys-init'],64)):
            row=subprocess.run([sys.executable,'-B','scripts/fs_session.py',*arguments],capture_output=True,text=True,timeout=10)
            self.assertEqual(row.returncode,status,row.stdout+row.stderr)
            self.assertNotIn('[RUNNING]',row.stderr)
