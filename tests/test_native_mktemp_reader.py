# SPDX-License-Identifier: BSD-2-Clause
"""Execute actual bounded-output syscall/query/reset bodies; no guest claim."""
from pathlib import Path
import os
import sys
import time
import unittest

from test_native_cleanup import block, af09_prelude, af09_command

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'sys-init/scripts'))
from bounded_capture import OwnedTemporaryDirectory, run_capture_bytes

COMMANDS = []
SCAFFOLD = r'''
const std=@import("std");
const options=@import("build_options");
const mktemp_reader=options.native_mktemp_reader;
const Frame=struct{rax:u64=0x10001,rdi:u64=1,rsi:u64=0x1000,rdx:u64=8};
const State=struct{
    OUTPUT_FIELD
    output_count:usize=0,generation:u64=1,app_binding:struct{value:u8=7}=.{},
};
var states:[4]State=@splat(.{});
var active:usize=0;
var user:[32]u8=@splat(90);
var response:i64=99;
var notes:usize=0;
var last_note:[160]u8=@splat(0);
const external_backing=false;
const service_memory=false;
const service_workers=false;
const backing_boot_views=@compileError("unexpected external reset branch");
const backing_partitions=@compileError("unexpected external reset branch");
const backingOwner=@compileError("unexpected external reset branch");
const bindPayload=@compileError("unexpected external reset branch");
const bindRecords=@compileError("unexpected external reset branch");
const bindChildren=@compileError("unexpected external reset branch");
fn require(ok:bool)void{std.debug.assert(ok);}
fn result(_: *State,value:i64)void{response=value;}
fn byte(_: *State,address:usize,_:bool)?*u8{
 return if(address>=0x1000 and address-0x1000<user.len)&user[address-0x1000] else null;
}
const serial=struct{fn write(value:[]const u8)void{
 notes+=1;@memset(&last_note,0);@memcpy(last_note[0..value.len],value);
}};
fn clear(slot:usize)void{states=@splat(.{});active=slot;response=99;notes=0;last_note=@splat(0);}
fn writeFrame(frame:*const Frame)void{
 const s=&states[active];
 switch(frame.rax){ WRITE_BODY,else=>unreachable, }
}
fn query(offset:u64)i64{
 const frame=&Frame{.rsi=offset};const s=&states[active];const caller=s;
 switch(@as(u64,0x20003)){ QUERY_BODY,else=>unreachable, }
 return response;
}
'''
CASES = r'''
test "actual output capacity default selected engine and other slots" {
 if(options.native_no_output)return;
 for(0..states.len) |slot| {
  clear(slot);const count:usize=if(options.native_mktemp_reader and slot==0)40 else 32;
  for(0..count) |_|{writeFrame(&.{});try std.testing.expectEqual(@as(i64,8),response);}
  try std.testing.expectEqual(count*8,states[slot].output_count);
  try std.testing.expectEqual(count,notes);
  try std.testing.expect(std.mem.indexOf(u8,&last_note,if(count==40)"offset=312 byte=90" else "offset=248 byte=90")!=null);
  const before=states[slot];writeFrame(&.{});
  try std.testing.expectEqual(@as(i64,-28),response);
  try std.testing.expect(std.meta.eql(before,states[slot]));
  try std.testing.expectEqual(count,notes);
  try std.testing.expectEqual(@as(i64,90),query(count*8-1));
  try std.testing.expectEqual(@as(i64,-11),query(count*8));
  try std.testing.expectEqual(@as(i64,-11),query(320));
 }
}
test "actual authority pointer request and transfer denials preserve state" {
 clear(0);
 if(options.native_no_output){
  const before=states[0];writeFrame(&.{});try std.testing.expectEqual(@as(i64,-13),response);
  try std.testing.expect(std.meta.eql(before,states[0]));try std.testing.expectEqual(@as(usize,0),notes);return;
 }
 for([_]Frame{.{.rdi=2},.{.rdx=257},.{.rsi=std.math.maxInt(u64),.rdx=8},.{.rsi=0x101c,.rdx=8}}) |frame| {
  const before=states[0];writeFrame(&frame);
  try std.testing.expectEqual(@as(i64,if(frame.rdi==2)-9 else -14),response);
  try std.testing.expect(std.meta.eql(before,states[0]));try std.testing.expectEqual(@as(usize,0),notes);
 }
 writeFrame(&.{.rdx=256});try std.testing.expectEqual(@as(i64,16),response);
 try std.testing.expectEqual(@as(usize,16),states[0].output_count);
 try std.testing.expectEqual(@as(usize,0),notes);
 const before=states[0];writeFrame(&.{.rdx=0});try std.testing.expectEqual(@as(i64,0),response);
 try std.testing.expect(std.meta.eql(before,states[0]));
}
test "actual generation reset clears every retained byte including expanded tail" {
 clear(0);@memset(&states[0].output,165);states[0].output_count=states[0].output.len;
 resetState(&states[0]);
 try std.testing.expectEqual(@as(usize,0),states[0].output_count);
 try std.testing.expect(std.mem.allEqual(u8,&states[0].output,0));
 try std.testing.expectEqual(@as(i64,-11),query(0));
 try std.testing.expectEqual(@as(i64,-11),query(320));
}
'''


class NativeMktempReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deadline = time.monotonic()+300

    def run_owned(self, argv, owner):
        result = run_capture_bytes(list(map(str,argv)),cwd=ROOT,timeout=60,deadline=self.deadline,
            owner=owner,record_path=Path(owner.name)/('child-'+str(len(COMMANDS))+'.process.json'),
            env={**os.environ,'LC_ALL':'C','TMPDIR':owner.name})
        COMMANDS.append(dict(argv=list(map(str,argv)),process=result.record,
                             stdout=result.stdout.decode(errors='replace')[-2000:],stderr=result.stderr.decode(errors='replace')[-4000:]))
        return result

    def test_actual_write_query_and_reset_bodies(self):
        source = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        field = next(line.strip() for line in source.splitlines() if line.strip().startswith('output: ['))
        scaffold = SCAFFOLD.replace('OUTPUT_FIELD',field).replace('WRITE_BODY',block(source,'        0x10000 + 1 => {'))
        scaffold = scaffold.replace('QUERY_BODY',block(source,'        0x20003 => {'))
        text = scaffold+af09_prelude(source)+block(source,'fn resetState(')+CASES
        with OwnedTemporaryDirectory(prefix='mktemp-output-',dir=os.environ.get('TMPDIR')) as owner:
            work = Path(owner.name)
            (work/'actual.zig').write_text(text)
            for selected,denied in ((False,False),(True,False),(True,True)):
                with self.subTest(selected=selected,denied=denied):
                    (work/'options.zig').write_text('pub const native_mktemp_reader='+str(selected).lower()+';\n'
                        'pub const native_no_output='+str(denied).lower()+';\n'
                        'pub const native_service_block=true;\n')
                    argv = af09_command(['zig','test','-OReleaseSafe','--cache-dir',work/'cache','--global-cache-dir',work/'global',
                        '--dep','build_options','-Mroot='+str(work/'actual.zig'),'-Mbuild_options='+str(work/'options.zig')])
                    observed = self.run_owned(argv,owner)
                    self.assertEqual(observed.returncode,0,observed.stdout.decode()+observed.stderr.decode())


    def test_actual_build_selection_guard(self):
        source = (ROOT/'build.zig').read_text()
        start = source.index('    if (native_mktemp_reader and (')
        guard = source[start:source.index(';',start)+1]
        # Keep the actual selection condition. Replace only its fatal rejection
        # leaf so a host test can inspect all refused configurations in one run.
        marker = '@panic("mktemp reader capture requires its exact private BSP read-only block profile");'
        self.assertEqual(guard.count(marker),1)
        guard = guard.replace(marker,'return false;')
        required = ('native_memory','native_memory_large','native_image_large','native_backing',
                    'native_service_memory','native_threads','native_thread_pair','native_thread_reuse',
                    'native_thread_origin','native_service_workers','native_clock','native_entropy',
                    'native_rtc','native_service_block','service_cleanup_trace')
        forbidden = ('release_artifact','smp','native_fs_session','native_session_lifecycle','native_service_channel',
                     'service_zpl_budget','service_lifetime','native_init_sustained','native_pipeline_capacity',
                     'native_process_freeze','native_runner_local','native_exec_denial','af09_diagnostic')
        fields = ('native_mktemp_reader',*required,*forbidden)
        data = 'const std=@import("std");\nconst Profile=struct{native_c_image:?[]const u8="image",\n'
        data += ''.join(name+':bool='+str(name not in forbidden).lower()+',\n' for name in fields)+'};\n'
        data += 'fn accepted(p:Profile)bool{const native_c_image=p.native_c_image;\n'
        data += ''.join('const '+name+'=p.'+name+';\n' for name in fields)+guard+'\nreturn true;}\n'
        data += 'test "actual private reader build selection" {\n'
        data += 'try std.testing.expect(accepted(.{}));\ntry std.testing.expect(!accepted(.{.native_c_image=null}));\n'
        for name in required:
            data += 'try std.testing.expect(!accepted(.{.'+name+'=false}));\n'
        for name in forbidden:
            data += 'try std.testing.expect(!accepted(.{.'+name+'=true}));\n'
        data += 'try std.testing.expect(accepted(.{.native_mktemp_reader=false,.native_c_image=null,.release_artifact=true,.smp=true}));\n}\n'
        with OwnedTemporaryDirectory(prefix='mktemp-reader-profile-',dir=os.environ.get('TMPDIR')) as owner:
            work = Path(owner.name)
            (work/'guard.zig').write_text(data)
            observed = self.run_owned(['zig','test','-OReleaseSafe','--cache-dir',work/'cache',
                                      '--global-cache-dir',work/'global',work/'guard.zig'],owner)
            self.assertEqual(observed.returncode,0,observed.stdout.decode()+observed.stderr.decode())



if __name__ == '__main__':
    unittest.main()
