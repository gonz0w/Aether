# SPDX-License-Identifier: BSD-2-Clause
"""Actual ABI31 wait producer preserves record boundaries, not UART hardware QA."""
from pathlib import Path
import tempfile
import unittest
from test_native_cleanup import block
from test_fs_owner_data import ROOT,run


class Framing(unittest.TestCase):
    def test_actual_wait_producer_selected_old_disabled_and_omitted_boundary(self):
        source=block((ROOT/'kernel/arch/x86_64/native_c.zig').read_text(),'fn traceStorageChannelWait(')
        base=r'''
const std=@import("std");
const State=struct{generation:u64=1};
const states=[_]State{.{},.{},.{},.{},.{},.{},.{.generation=0}};
const serial=struct{
 var bytes:[4096]u8=undefined;var used:usize=0;
 fn write(data:[]const u8)void{@memcpy(bytes[used..][0..data.len],data);used+=data.len;}
};
'''
        checks=r'''
test "actual record remains independently parseable after partial application output"{
 for([_]usize{0,1,2,6})|owner|for([_][]const u8{"park","wake"})|phase|for([_]i64{0,-4})|status|{
  for([_][]const u8{"","$ ","getcwd() failed:","partial without newline","done\n"})|prefix|{
   serial.used=0;serial.write(prefix);traceStorageChannelWait(owner,phase,status);
   if(!@import("build_options").native_service_channel_wait){
    try std.testing.expectEqualStrings(prefix,serial.bytes[0..serial.used]);continue;
   }
   var buffer:[256]u8=undefined;
   const row=try std.fmt.bufPrint(&buffer,"NATIVE STORAGE WAIT slot={d} generation={d} phase={s} status={d}\n",.{owner,states[owner].generation,phase,status});
   if(combined_owner_stack){
    // Independent consumer requires the emitted record to begin at column0.
    var lines=std.mem.splitScalar(u8,serial.bytes[0..serial.used],'\n');var count:usize=0;
    while(lines.next())|line|if(std.mem.eql(u8,line,row[0..row.len-1])){count+=1;};
    try std.testing.expectEqual(@as(usize,1),count);
    try std.testing.expectEqualStrings(prefix,serial.bytes[0..prefix.len]);
   }else{
    try std.testing.expectEqualStrings(prefix,serial.bytes[0..prefix.len]);
    try std.testing.expectEqualStrings(row,serial.bytes[prefix.len..serial.used]);
   }
  }
 };
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-af07-framing-') as folder:
            out=Path(folder)
            for name,selected,enabled,body,status in [
                ('selected',True,True,source,0),('old',False,True,source,0),
                ('disabled',True,False,source,0),
                ('omission',True,True,source,1)]:
                # Source contains an escaped newline literal, not a literal LF.
                if name=='omission':body=source.replace('if (combined_owner_stack) serial.write("\\n");','{}');self.assertNotEqual(body,source)
                with self.subTest(name=name):
                    (out/'options.zig').write_text('pub const native_service_channel_wait='+str(enabled).lower()+';')
                    (out/'test.zig').write_text(base+'const combined_owner_stack='+str(selected).lower()+';'+body+checks)
                    log=run(['zig','test','--cache-dir',out/'cache','--global-cache-dir',out/'global','--dep','build_options',
                        '-Mroot='+str(out/'test.zig'),'-Mbuild_options='+str(out/'options.zig')],out,status)
                    self.assertNotRegex(log,r':\d+:\d+: error:')
                    if status:self.assertIn('FAIL',log)
