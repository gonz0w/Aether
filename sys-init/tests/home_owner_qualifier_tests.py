# SPDX-License-Identifier: BSD-2-Clause
"""Controlled transcripts exercise parsers only; no guest/media acceptance."""
import copy
import ast
import inspect
import tempfile
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('home_owner_qualifier',ROOT/'sys-init/scripts/qualify-home-owner.py')
qualifier=importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualifier)

GEOMETRY=dict(engine_pages=1337,shell_pages=80,helper_pages=35,owner_bytes=47384)


def reader_text(digest=bytes(range(32)),engine_pages=1300):
    rows=[]
    for generation in range(1,4):
        rows.append(f'NATIVE MEMORY admitted slot=0 generation={generation} used={engine_pages} remaining={8192-engine_pages}')
        phases=digest if generation==1 else b'BNR'
        rows += [f'NATIVE observation slot=0 generation={generation} offset={i*8} byte={value}' for i,value in enumerate(phases)]
        rows.append(f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0')
        rows += [f'NATIVE CLEANUP v=1 slot=0 generation={generation} phase={phase} selected={0 if phase==1 else 2} pages=8192 reclaimed={generation if phase==7 else generation-1}' for phase in range(1,8)]
    rows += ['NATIVE supervisor result=100 reclaimed=3','AETHER NATIVE BLOCK PASS']
    return '\n'.join(rows)+'\n'


def writer_text(geometry=GEOMETRY):
    rows=[f'NATIVE MEMORY admitted slot=0 generation=1 used={geometry["engine_pages"]} remaining={8192-geometry["engine_pages"]}',
          f'NATIVE MEMORY admitted slot=1 generation=1 used={geometry["shell_pages"]} remaining={128-geometry["shell_pages"]}',
          'AF09-BEGIN',
          f'NATIVE MEMORY admitted slot=2 generation=1 used={geometry["helper_pages"]} remaining={128-geometry["helper_pages"]}',
          'AF09-HOME-WR', 'NATIVE terminal slot=2 generation=1 kind=1 detail=7']
    for slot in (0,1,2,6):
        generation=int(slot!=6)
        rows += [f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0' for phase in ('park','wake')]
    for slot,pages,prior in ((2,128,0),(1,128,1),(0,8192,2)):
        if slot==1:rows += ['AF09-STATUS:7','NATIVE terminal slot=1 generation=1 kind=1 detail=0']
        if slot==0:rows += ['NATIVE terminal slot=0 generation=1 kind=1 detail=0']
        rows += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+int(phase==7)}' for phase in range(1,8)]
    rows += ['NATIVE init halted ticks=2345 idle=123 reclaimed=3','AETHER NATIVE BLOCK PASS']
    return '\n'.join(rows)+'\n'


def snapshot(digest):
    return dict(status='captured',sha256=digest*64,bytes=1024*1024*1024+8192,
                region_sha256='6f3ded903a6bb2f9baaecc64359fe464910b4b7d003e5e7054768e54fe3f65d2' if digest=='1' else digest*64,
                outside_region_canaries_match=True)


class HomeOwnerQualifier(unittest.TestCase):
    def test_full_digest_and_reuse_cleanup(self):
        expected=bytes((i*17)&255 for i in range(32))
        row=qualifier.reader_trace(reader_text(expected),1300)
        self.assertEqual(row['metadata_sha256'],expected.hex())
        self.assertEqual(row['reclaimed'],3)
        self.assertFalse(row['native_executed'])

    def test_every_reader_expected_row_is_required_and_unique(self):
        lines=reader_text().splitlines()
        for index in range(len(lines)):
            with self.subTest(line=index):
                for changed in (lines[:index]+lines[index+1:],lines[:index]+[lines[index]]+lines[index:]):
                    with self.assertRaises(ValueError):qualifier.reader_trace('\n'.join(changed)+'\n',1300)

    def test_reader_extra_malformed_wrong_generation_offset_status_denied(self):
        text=reader_text()
        for changed in (text.replace('offset=248','offset=249'),text.replace('byte=31','byte=256'),
            text.replace('generation=3 offset=16','generation=4 offset=16'),
            text.replace('detail=0','detail=7',1),text.replace('used=1300','used=1329',1),
            text.replace('reclaimed=3\nAETHER','reclaimed=2\nAETHER'),
            text+'NATIVE observation malformed\n',text+'NATIVE terminal malformed\n',
            text.replace('AETHER NATIVE BLOCK PASS','AETHER PANIC: failure')):
            with self.subTest(changed=changed[-140:]),self.assertRaises(ValueError):qualifier.reader_trace(changed,1300)

    def test_writer_exact_new_measured_geometry_workload_and_cleanup(self):
        row=qualifier.writer_trace(writer_text(),GEOMETRY)
        self.assertEqual(row['child_status'],7)
        self.assertEqual(row['provider_attempts'],3)
        self.assertEqual(row['primary_channel_waits'],4)
        self.assertFalse(row['native_executed'])

    def test_every_writer_event_is_required_and_unique(self):
        lines=writer_text().splitlines()
        for index in range(len(lines)):
            for changed in (lines[:index]+lines[index+1:],lines[:index]+[lines[index]]+lines[index:]):
                with self.subTest(line=index),self.assertRaises(ValueError):qualifier.writer_trace('\n'.join(changed)+'\n',GEOMETRY)

    def test_writer_old_geometry_markers_bad_waits_and_extra_rows_reject(self):
        text=writer_text()
        for changed in (text.replace('used=1337 remaining=6855','used=1329 remaining=6863'),
            text.replace('AF09-HOME-WR','AF07-READ:ok'),text.replace('AF09-STATUS:7','AF09-STATUS:0'),
            text.replace('ticks=2345','ticks=6001'),text.replace('phase=wake status=0','phase=wake status=1',1),
            text+'NATIVE terminal malformed\n',text.replace('AF09-BEGIN','AF09-BEGIN\nAF09-HOME-WR')):
            with self.assertRaises(ValueError):qualifier.writer_trace(changed,GEOMETRY)
        for field in ('engine_pages','shell_pages','helper_pages','owner_bytes'):
            bad=dict(GEOMETRY);bad[field]=0
            with self.assertRaises(ValueError):qualifier.writer_trace(text,bad)

    def sequence(self):
        pristine=snapshot('1');written=snapshot('2')
        readers=[qualifier.reader_trace(reader_text(),1300) for _ in range(2)]
        media=[dict(role=role,before=copy.deepcopy(before),after=copy.deepcopy(after),vm_stop_confirmed=True,vm_run_returned=True) for role,before,after in (
            ('pristine',pristine,pristine),('writer',pristine,written),('recovery',written,written))]
        return readers[0],qualifier.writer_trace(writer_text(),GEOMETRY),readers[1],media

    def test_full_metadata_comparison_checks_every_byte(self):
        args=self.sequence()
        self.assertEqual(qualifier.qualify_sequence(*args)['metadata_sha256'],bytes(range(32)).hex())
        for index in range(32):
            changed=copy.deepcopy(args)
            digest=bytearray.fromhex(changed[2]['metadata_sha256']);digest[index]^=1
            changed[2]['metadata_sha256']=digest.hex()
            with self.subTest(byte=index),self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                qualifier.qualify_sequence(*changed)

    def test_media_order_full_identity_canaries_stop_and_reader_unchanged_are_required(self):
        args=self.sequence()
        for name,alter in (
            ('order',lambda a:a[3].reverse()),
            ('stop',lambda a:a[3][1].update(vm_stop_confirmed=False)),
            ('not-run',lambda a:a[3][1].update(vm_run_returned=False)),
            ('baseline-region',lambda a:a[3][0]['before'].update(region_sha256='f'*64)),
            ('guards',lambda a:a[3][2]['after'].update(outside_region_canaries_match=False)),
            ('extent',lambda a:a[3][2]['after'].update(bytes=1024**3)),
            ('writer-unchanged',lambda a:a[3][1].update(after=a[3][1]['before'])),
            ('recovery-mutates',lambda a:a[3][2]['after'].update(sha256='f'*64)),
            ('reader-cleanup',lambda a:a[2].update(reclaimed=2)),
            ('writer-status',lambda a:a[1].update(child_status=0)),
            ('writer-attempts',lambda a:a[1].update(provider_attempts=2))):
            changed=copy.deepcopy(args);alter(changed)
            with self.subTest(control=name),self.assertRaises(ValueError):qualifier.qualify_sequence(*changed)

    def test_firmware_carriage_return_does_not_weaken_native_row_format(self):
        qualifier.reader_trace('firmware\r\n'+reader_text(),1300)
        with self.assertRaises(ValueError):
            qualifier.reader_trace(reader_text().replace('offset=248 byte=31\n','offset=248 byte=31\r\n'),1300)

    def test_intake_forwards_one_explicit_deadline(self):
        record=dict(format=qualifier.inputs.SCHEMA,profile=qualifier.inputs.PROFILE,
                    bounds=qualifier.inputs.BOUNDS,admission=dict(GEOMETRY))
        with patch.object(qualifier.inputs,'intake',return_value=dict(format=qualifier.inputs.SCHEMA)) as intake, \
             patch.object(qualifier.inputs,'read_json',return_value=record), \
             patch.object(qualifier.time,'monotonic',return_value=10):
            self.assertEqual(qualifier.input_record(Path('/controlled'), '0'*64, deadline=20),record)
            intake.assert_called_once_with(Path('/controlled'),'0'*64,deadline=20)

    def test_expired_budget_stops_before_intake(self):
        with patch.object(qualifier.inputs,'intake') as intake, \
             patch.object(qualifier.time,'monotonic',return_value=20):
            with self.assertRaisesRegex(RuntimeError,'deadline'):
                qualifier.input_record(Path('/controlled'),'0'*64,deadline=20)
            intake.assert_not_called()

    def test_intake_that_consumes_remaining_budget_cannot_continue(self):
        with patch.object(qualifier.inputs,'intake',return_value={}) as intake, \
             patch.object(qualifier.inputs,'read_json') as read, \
             patch.object(qualifier.time,'monotonic',side_effect=[10,20]):
            with self.assertRaisesRegex(RuntimeError,'deadline'):
                qualifier.input_record(Path('/controlled'),'0'*64,deadline=20)
            intake.assert_called_once_with(Path('/controlled'),'0'*64,deadline=20)
            read.assert_not_called()

    def test_prepare_starts_the_total_budget_before_first_intake(self):
        with patch.object(qualifier,'input_record',side_effect=RuntimeError('CONTROL_STOP_BEFORE_EFFECT')) as intake, \
             patch.object(qualifier.time,'monotonic',return_value=1000):
            with self.assertRaisesRegex(RuntimeError,'CONTROL_STOP_BEFORE_EFFECT'):
                qualifier.prepare(Path('/controlled'),'0'*64)
            intake.assert_called_once_with(Path('/controlled'),'0'*64,deadline=2800)

    def test_compiler_artifact_limit_exceeds_diagnostic_cap_and_existing_engine(self):
        proc=qualifier.owned_process()
        artifact_limit=inspect.signature(proc.run).parameters['file_limit'].default
        size=(ROOT/'.deps/fs-launch-af07-2026-10-21-v5/filesystem.elf').stat().st_size
        self.assertGreater(size,qualifier.DIAGNOSTIC_LIMIT)
        self.assertGreater(artifact_limit,size)
        tree=ast.parse(inspect.getsource(qualifier.prepare))
        calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)
               and isinstance(node.func,ast.Attribute) and node.func.attr=='run']
        self.assertEqual(len(calls),1)
        self.assertNotIn('file_limit',{kw.arg for kw in calls[0].keywords})

    def test_only_direct_rust_tools_receive_private_llvm_environment(self):
        tools=__import__('json').loads((ROOT/'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json').read_text())['tools']
        proc=qualifier.owned_process()
        for name in ('clang','rustc','clippy-driver','rustfmt','nm','readelf'):
            env=qualifier.child_environment(proc,Path('/controlled'),tools,[tools[name]['path']])
            with self.subTest(tool=name):
                if name in ('rustc','clippy-driver','rustfmt'):
                    self.assertEqual(env['DYLD_LIBRARY_PATH'],str(Path(tools['rustc']['path']).parent.parent/'lib'))
                else:self.assertNotIn('DYLD_LIBRARY_PATH',env)

    def test_only_known_linker_denials_accept_exact_exit_one(self):
        for marker in qualifier.launch.LINK_DENIALS:
            process=dict(complete=True,cleanup='complete',exit=1)
            self.assertTrue(qualifier.command_accepted(1,'linker: '+marker+'\n',process,marker))
            for code in (0,-9,2):
                with self.subTest(marker=marker,code=code):
                    self.assertFalse(qualifier.command_accepted(code,marker,dict(process,exit=code),marker))
            self.assertFalse(qualifier.command_accepted(1,'other failure',process,marker))
        self.assertFalse(qualifier.command_accepted(1,'unknown marker',dict(complete=True,cleanup='complete',exit=1),'unknown marker'))

    def test_command_acceptance_always_requires_complete_cleanup_and_matching_status(self):
        marker=next(iter(qualifier.launch.LINK_DENIALS))
        for change in (dict(complete=False),dict(complete=1),dict(cleanup='unresolved'),dict(exit=-9)):
            process=dict(complete=True,cleanup='complete',exit=1);process.update(change)
            self.assertFalse(qualifier.command_accepted(1,marker,process,marker))
        self.assertTrue(qualifier.command_accepted(0,'',dict(complete=True,cleanup='complete',exit=0)))
        self.assertFalse(qualifier.command_accepted(1,'',dict(complete=True,cleanup='complete',exit=1)))

    def test_explicit_external_lld_does_not_receive_rust_private_llvm(self):
        tools=__import__('json').loads((ROOT/'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json').read_text())['tools']
        proc=qualifier.owned_process()
        for flags in (['-C','linker='+tools['lld']['path']],['-Clinker='+tools['lld']['path']]):
            env=qualifier.child_environment(proc,Path('/controlled'),tools,[tools['rustc']['path'],*flags])
            self.assertNotIn('DYLD_LIBRARY_PATH',env)
        ordinary=qualifier.child_environment(proc,Path('/controlled'),tools,[tools['rustc']['path'],'--emit=obj'])
        self.assertIn('DYLD_LIBRARY_PATH',ordinary)

    def test_full_boundary_hashes_reject_retained_change_after_controlled_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);source=work/'retained';runtime=work/'runtime';tool=work/'tool'
            source.write_bytes(b'frozen');runtime.write_bytes(b'owned runtime');tool.write_bytes(b'executable identity')
            retained={str(source):qualifier.digest(source)};generated={str(runtime):qualifier.digest(runtime)}
            tools={'controlled':dict(path=str(tool),sha256=qualifier.digest(tool))};record={}
            qualifier.verify_boundary(retained,generated,record,'before-consumer')
            qualifier.verify_child([str(tool)],tools,generated)
            # Controlled child callback, not a build or guest: mutation must
            # invalidate the whole consumer before any candidate publication.
            source.write_bytes(b'changed during controlled callback')
            qualifier.verify_child([str(tool)],tools,generated)
            with self.assertRaisesRegex(ValueError,'changed'):
                qualifier.verify_boundary(retained,generated,record,'after-consumer')
            self.assertEqual(record['input_boundaries'][0]['status'],'pass')
            self.assertEqual(record['input_boundaries'][-1]['status'],'failed')

    def test_child_checks_actual_tool_and_generated_runtime_every_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);runtime=work/'runtime';tool=work/'tool'
            runtime.write_bytes(b'runtime');tool.write_bytes(b'tool')
            generated={str(runtime):qualifier.digest(runtime)};tools={'controlled':dict(path=str(tool),sha256=qualifier.digest(tool))}
            qualifier.verify_child([str(tool)],tools,generated)
            runtime.write_bytes(b'corrupted')
            with self.assertRaises(ValueError):qualifier.verify_child([str(tool)],tools,generated)
            runtime.write_bytes(b'runtime');tool.write_bytes(b'changed tool')
            with self.assertRaises(ValueError):qualifier.verify_child([str(tool)],tools,generated)
            with self.assertRaises(ValueError):qualifier.verify_child([str(work/'unselected')],tools,{})

    def test_shared_controller_artifact_is_exact_and_precedes_reader_preparation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'controller.raw';path.write_bytes(b'exact controller')
            selected=dict(path=str(path),sha256=qualifier.digest(path),bytes=path.stat().st_size,
                          source_sha256=qualifier.digest(qualifier.CONTROLLER))
            self.assertEqual(qualifier.controller_bytes(selected),b'exact controller')
            path.write_bytes(b'changed controller')
            with self.assertRaises(ValueError):qualifier.controller_bytes(selected)
        tree=ast.parse(inspect.getsource(qualifier.prepare))
        order=[node.func.id for node in sorted((node for node in ast.walk(tree)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)),key=lambda node:node.lineno)]
        self.assertEqual(order.count('build_controller'),1)
        self.assertLess(order.index('build_controller'),order.index('build_reader'))

    def test_no_execution_entrypoint_and_original_controller_unchanged(self):
        self.assertFalse(hasattr(qualifier,'guest'))
        self.assertFalse(hasattr(qualifier,'execute'))
        original=ROOT/'user/storage/session/readback.rs'
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),qualifier.ORIGINAL_CONTROLLER_SHA256)
        self.assertEqual(qualifier.RTC,'2026-10-06T12:34:00,clock=vm')


if __name__=='__main__':unittest.main()
