# SPDX-License-Identifier: BSD-2-Clause
"""Execute actual private owner event/clock bodies; no host uptime claim."""
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
from test_native_cleanup import block
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import storage_lifetime as profile
SCAFFOLD='''
var admission_failed=false;const service_memory=true;const combined_profile=false;const combined_application_profile=false;const combined_init=false;const combined_owner_data=false;const combined_owner_stack=false;
const FsSession=struct{const magic="AENFS002";const init_magic="AENFS003";const owner_data_magic="AENFS004";};var block_closed=false;
fn require(ok:bool)void{admission_failed=admission_failed or !ok;}
const std=@import("std");const TickProjectionError=error{Overflow};const Sustained=@import("events");
const Frame=struct{rax:u64=0,rdi:u64=0,rsi:u64=0,rdx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0};
const State=struct{admitted:bool=false,frame:Frame=.{},
 fn context(s:*State) *State{return s;}
};
var states:[2]State=@splat(.{});var active:usize=1;var total_ticks:usize=7000;
var sustained=false;var session_lifecycle=false;var sustained_events:Sustained.Events=.{};
var console_closed=false;var serial_reads:usize=0;var rotations:usize=0;
var channels:[1]struct{owners:[2]?usize=.{null,null},stream:struct{count:usize=0}=.{}}=@splat(.{});
var idle_ticks:usize=0;var reclaimed:usize=0;
const serial=struct{
 fn inputReady() bool {serial_reads+=1;return true;}
 fn write(_:[]const u8) void{}
 fn halt() noreturn {@panic("UNEXPECTED_HALT");}
};
fn supervisorSlot() usize{return 1;}fn workerCount() usize{return 1;}fn channelCount() usize{return 1;}
fn result(s:*State,n:i64) void{s.frame.rax=@bitCast(n);}
fn select() *const Frame{return &states[active].frame;}
fn rotate() void{rotations+=1;}
fn code(f:*const Frame) i64{return @bitCast(f.rax);}
'''
CASES='''
test "actual selected magic and signed clock projection" {
 const selected=storageLifetime();
 try std.testing.expectEqualStrings(if(selected) "AENBD005" else "AENBD004",storageMagic());
 var envelope:[48]u8=@splat(0);
 for([_] []const u8{"AENBD003","AENBD004","AENBD005","AENBD006"}) |magic| {
  @memcpy(envelope[0..8],magic);try std.testing.expectEqual(std.mem.eql(u8,magic,storageMagic()),admit(&envelope));
 }
 try std.testing.expectEqual(@as(i64,0),try tickNanoseconds(0));
 try std.testing.expectEqual(@as(i64,65000000000),try tickNanoseconds(6500));
 const last:usize=std.math.maxInt(i64)/10000000;
 try std.testing.expectEqual(@as(i64,@intCast(last*10000000)),try tickNanoseconds(last));
 try std.testing.expectError(error.Overflow,tickNanoseconds(last+1));
 try std.testing.expectError(error.Overflow,tickNanoseconds(std.math.maxInt(usize)));
}
test "actual storage owner denies workers foreign authority unused args and halt" {
 if(!storageLifetime())return;
 var f:Frame=.{.rax=0x2a000,.rdi=0xe002};active=0;
 try std.testing.expectEqual(@as(i64,-13),code(sustainedOperation(&f)));
 active=1;f.rdi=0xe003;try std.testing.expectEqual(@as(i64,-13),code(sustainedOperation(&f)));
 f.rdi=0xe002;f.r10=1;try std.testing.expectEqual(@as(i64,-22),code(sustainedOperation(&f)));
 f.r10=0;f.rax=0x2a002;f.rdi=0xf002;
 try std.testing.expectEqual(@as(i64,-38),code(sustainedOperation(&f)));
 try std.testing.expectEqual(@as(usize,0),serial_reads);
 try std.testing.expect(!sustained_events.occupied);
}
test "actual storage park stays idle without console input and deadline completes exact frame" {
 if(!storageLifetime())return;
 states=@splat(.{});active=1;total_ticks=7000;sustained_events=.{};serial_reads=0;rotations=0;
 const snapshot=sustainedOperation(&.{.rax=0x2a000,.rdi=0xe002});
 try std.testing.expectEqual(@as(i64,0),code(snapshot));try std.testing.expectEqual(@as(u64,7000),snapshot.r8);
 const parked=sustainedOperation(&.{.rax=0x2a001,.rdi=0xe002,.rsi=snapshot.rdx,.rdx=13500});
 _=parked;try std.testing.expect(sustained_events.parked());try std.testing.expectEqual(@as(usize,1),rotations);
 total_ticks=13499;refreshSustained();try std.testing.expect(sustained_events.parked());
 total_ticks=13500;refreshSustained();try std.testing.expect(!sustained_events.occupied);
 try std.testing.expectEqual(@as(i64,-110),code(&states[1].frame));
 try std.testing.expectEqual(@as(u64,13500),states[1].frame.r8);
 try std.testing.expectEqual(@as(usize,0),serial_reads);
 states[1].frame.rax=99;refreshSustained();try std.testing.expectEqual(@as(u64,99),states[1].frame.rax);
}
test "old init halt still requires console closure" {
 if(storageLifetime())return;
 states=@splat(.{});active=1;sustained=true;console_closed=false;sustained_events=.{};
 try std.testing.expectEqual(@as(i64,-16),code(sustainedOperation(&.{.rax=0x2a002,.rdi=0xf002})));
}
'''


class StorageLifetime(unittest.TestCase):
    def test_actual_kernel_bodies_and_compiling_failure_controls(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        prefix=native[native.index('    require(envelope.len > 40);'):native.index('    const direct_native =')]
        admission='fn admit(envelope:[]const u8)bool{admission_failed=false;\n'+prefix+'\nreturn !admission_failed;}\n'
        bodies=admission+'\n'+'\n'.join(block(native,'fn '+n+'(') for n in ('lifecycleEnabled','storageLifetime','ownerEventsEnabled','storageMagic','tickNanoseconds','refreshSustained','sustainedOperation'))
        variants=[('old',False,bodies),('storage',True,bodies),
          ('authority-omitted',True,bodies.replace('active != supervisorSlot() or f.rdi !=','false or f.rdi !=',1)),
          ('serial-leak',True,bodies.replace('!storageLifetime() and !console_closed','!console_closed')),
          ('clock-range',True,bodies.replace('if (ns > std.math.maxInt(i64)) return error.Overflow;','if (false) return error.Overflow;'))]
        with tempfile.TemporaryDirectory(prefix='aether-storage-lifetime-kernel-') as folder:
            out=Path(folder)
            for name,selected,source in variants:
                with self.subTest(name=name):
                    (out/'options.zig').write_text(f'pub const native_service_lifetime={str(selected).lower()};pub const native_service_channel_wait=true;pub const native_service_block=true;pub const native_service_channel=true;')
                    (out/'test.zig').write_text(SCAFFOLD+source+CASES)
                    r=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','build_options','--dep','events','-Mroot='+str(out/'test.zig'),'-Mbuild_options='+str(out/'options.zig'),'-Mevents='+str(ROOT/'kernel/native_sustained.zig')],capture_output=True,text=True,timeout=120)
                    if name in ('old','storage'):self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                    else:
                        self.assertNotEqual(r.returncode,0)
                        self.assertNotRegex(r.stderr,r':\d+:\d+: error:',r.stderr)

    def test_actual_rust_idle_and_compiling_omissions(self):
        original=(ROOT/'user/storage/service-runtime/fs-storage-lifecycle.rs').read_text()
        with tempfile.TemporaryDirectory(prefix='aether-storage-lifetime-owner-') as folder:
            out=Path(folder)
            for name,source in [('positive',original),('early',original.replace('tick >= deadline','tick >= previous',1)),('reset',original.replace('previous = tick;', 'previous = start;',1)),('hints',original.replace('0..32','0..31',1))]:
                (out/'test.rs').write_text(source)
                r=subprocess.run(['rustc','+1.98.0','--edition=2024','-Dwarnings','--test',str(out/'test.rs'),'-o',str(out/'test')],capture_output=True,text=True,timeout=60)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                r=subprocess.run([str(out/'test'),'--test-threads=1'],capture_output=True,text=True,timeout=10)
                if name=='positive':self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                else:self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)

    def test_trace_rejects_missing_early_repeated_overlap_and_regressing_rows(self):
        good='NATIVE STORAGE observe tick=1000\nNATIVE STORAGE park tick=1001 deadline=7500\nNATIVE STORAGE wake tick=7500 outcome=deadline\n'
        self.assertEqual(profile.trace('NATIVE STORAGE WAIT park slot=0\n'+good)['idle_delivered_ticks'],6500)
        for bad in ['',good.replace('tick=7500','tick=7499'),good.replace('6500','6499').replace('deadline=7500','deadline=7499'),good+good,good.split('\n',1)[1],good.replace('wake','park')]:
            with self.assertRaises(ValueError):profile.trace(bad)

    def test_actual_directory_controller_holds_read_alias_through_idle_and_keeps96_requests(self):
        from test_native_cleanup import block as body
        fixture=(ROOT/'tests/fixtures/fs_directory_client.rs').read_text()
        controller=(ROOT/'user/storage/service-runtime/fs-directories-client.rs').read_text()
        # Substitute only the scalar clock boundary. Its actual implementation
        # and kernel park body have independent executed tests above.
        controller=controller.replace('#[path = "fs-storage-lifecycle.rs"]\nmod storage_lifecycle;', 'mod storage_lifecycle {pub fn idle()->bool {crate::mock_idle()}}')
        fixture=fixture.replace('CONTROLLER','client.rs')
        fixture=fixture.replace('''            reply(0),
            reply(0),
            mutation(792, 0),''','''            reply(0),
            mutation(792, 0),''')
        fixture=fixture.replace('''        for _ in 0..64 {
            s.input.push_back(entry(1, 1, 5));
        }''','''        let mut h=reply(0);put(&mut h,5,4096);s.input.push_back(h);
        for offset in (0..4096).step_by(64) {
            let mut data=[0;64];for(i,b)in data.iter_mut().enumerate(){*b=(71+offset+i)as u8;}s.input.push_back(data);
        }
        s.input.push_back(reply(0));
        for _ in 0..63 { s.input.push_back(entry(1,1,5)); }
''')
        bad=body(fixture,'fn corrupted_reply_epoch_final_data_byte_or_parent_size_is_rejected(')
        fixture=fixture.replace(bad,'''fn corrupted_reply_epoch_final_data_byte_or_parent_size_is_rejected() {
            let c=setup();STATE.with(|s|{let mut s=s.borrow_mut();let i=s.input.len()-65;s.input[i][63]^=1;});
            assert!(std::panic::catch_unwind(||c.exercise()).is_err());
        }''')
        fixture+='''
fn mock_idle()->bool {
 STATE.with(|s|{
  let s=s.borrow();let mut frames=s.output.iter();let mut req=Vec::new();
  while let Some(h)=frames.next(){let op=get(h,1);req.push((op,get(h,3)));
   let length=if op==5{4096}else if matches!(op,1|7..=11){get(h,5)as u32 as usize+(get(h,5)>>32)as usize}else{0};
   for _ in(0..length).step_by(64){frames.next().unwrap();}
  }
  assert_eq!(req.last(),Some(&(11,5)),"IDLE_AFTER_SEVEN_MUTATIONS");
  assert!(req.contains(&(1,2)));assert!(!req.contains(&(3,4)),"READ_ALIAS_MUST_LIVE");assert!(!req.contains(&(7,5)),"STAGE_AFTER_IDLE");
 });true
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-storage-lifetime-transcript-') as folder:
            out=Path(folder);(out/'client.rs').write_text(controller);(out/'test.rs').write_text(fixture)
            r=subprocess.run(['rustc','+1.98.0','--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--cfg','fs_storage_lifetime','--test',str(out/'test.rs'),'-o',str(out/'test')],capture_output=True,text=True,timeout=60)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            r=subprocess.run([str(out/'test'),'--test-threads=1'],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_actual_pair_role_flags_oracle_and_kernel_identity_fail_closed(self):
        import copy
        from unittest.mock import patch
        from test_openzfs_fs_directories_service import Directories,SOURCE,DELIVERY
        import openzfs_fs_directories_service as dirs
        import zpl_pair as pair
        helper=Directories();f=helper.fixture('normal');self.addCleanup(helper.doCleanups)
        for role in ('writer','reader'):
            b=f.builds[role];b['storage_lifetime']=True
            b['port']['volume']['namespace_objects']['mixed-probe-source']=pair.hashlib.sha256(dirs.probe((SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',storage_lifetime=True).encode()).hexdigest()
        b=f.builds['writer'];b['commands'][0]['argv'].append('-Dnative-service-lifetime=true')
        b['commands'][1]['argv'][3:3]=['--cfg','fs_storage_lifetime']
        b['cases'][0]['kernel_profile']='AENBD005/owner27/engine26'
        helper.verify(f,'normal',storage_lifetime=True)
        original=copy.deepcopy(f.builds)
        for mode in ('reader-kernel','no-kernel','old-envelope','old-oracle','no-cfg'):
            f.builds=copy.deepcopy(original)
            if mode=='reader-kernel':f.builds['reader']['commands'][0]['argv'].append('-Dnative-service-lifetime=true')
            elif mode=='no-kernel':f.builds['writer']['commands'][0]['argv'].remove('-Dnative-service-lifetime=true')
            elif mode=='old-envelope':f.builds['writer']['cases'][0]['kernel_profile']='AENBD004/ABI26'
            elif mode=='old-oracle':f.builds['reader']['port']['volume']['namespace_objects']['mixed-probe-source']='0'*64
            else:
                args=f.builds['writer']['commands'][1]['argv'];i=args.index('fs_storage_lifetime');del args[i-1:i+1]
            with self.subTest(mode=mode),self.assertRaises(ValueError):helper.verify(f,'normal',storage_lifetime=True)

    def test_actual_watchdog120_requires_private_writer_and_preserves_stop_join(self):
        from unittest.mock import Mock,patch
        import native_smoke as native
        import zpl_pair as pair
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX,dir=ROOT/'zig-out') as folder:
            out=Path(folder);(out/'writer').mkdir();disk=out/'native-namespace.raw'
            with disk.open('wb') as stream:stream.truncate(1073750016)
            process=Mock();process.poll.return_value=None;process.wait.return_value=0
            common=dict(_pair_stop=True,_zpl_writer_60s=True,_storage_lifetime=True,block_namespace=True,block_large=True,block_disk=disk,marker=pair.MARKER.encode())
            for change in ({'_zpl_writer_60s':False},{'_storage_lifetime':120},{'_monitor_diagnostic':True},{'_zpl_mutation_seed':True}):
                with self.assertRaises(ValueError):native.run(out/'writer/aether.iso',**(common|change))
            with patch.object(native,'verify'),patch.object(native.subprocess,'check_output',return_value='QEMU emulator version '+native.LOCK['qemu']),patch.object(native.subprocess,'Popen',return_value=process),patch.object(native.shutil,'copyfile'),patch('openzfs_namespace.native_media_snapshot'),patch.object(native,'wait_for_boot',side_effect=TimeoutError('fixed120')) as wait:
                with self.assertRaises(TimeoutError):native.run(out/'writer/aether.iso',**common)
                self.assertEqual(wait.call_args.args[2],120)
            process.terminate.assert_called_once();process.wait.assert_called_once()
